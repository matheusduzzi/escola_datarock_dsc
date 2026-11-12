"""Divide os pedidos da Loja Exemplo em treino, validação e teste pela data do pedido.

    python3 particoes.py                           # grava particoes.csv e manifesto.txt
    python3 particoes.py --checar particoes.csv    # refaz a divisão e compara com um arquivo

A regra está nas datas de CORTES. O manifesto guarda a impressão digital (SHA-256) da base e
da lista de pedidos de cada parte. Com ele, outra pessoa refaz a divisão e vê se chegou às
mesmas partes. As saídas do teste não aparecem: ele fica fechado até a decisão final.
"""
import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd

BASE = Path("../dados/loja/pedidos.csv")
ARQUIVO = Path("particoes.csv")
MANIFESTO = Path("manifesto.txt")
PARTES = ["treino", "validação", "teste"]
# Último dia de cada parte. O teste vai até o fim da base.
CORTES = {"treino": "2026-03-31", "validação": "2026-05-31"}


def digital_da_base(caminho):
    """SHA-256 dos bytes da base, com fim de linha igual em qualquer sistema."""
    return hashlib.sha256(caminho.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def digital_dos_ids(ids):
    texto = "".join(f"{i}\n" for i in sorted(int(i) for i in ids))
    return hashlib.sha256(texto.encode("ascii")).hexdigest()[:12]


def ler_base():
    if not BASE.is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 05-treino-validacao-e-teste do kit.")
    return pd.read_csv(BASE, parse_dates=["data_pedido"])


def pela_regra(pedidos):
    parte = pd.Series("teste", index=pedidos.index)
    parte[pedidos["data_pedido"] <= CORTES["validação"]] = "validação"
    parte[pedidos["data_pedido"] <= CORTES["treino"]] = "treino"
    return parte


def manifesto(pedidos, parte):
    linhas = [
        f"base: {BASE.as_posix()}, {len(pedidos)} pedidos, de {pedidos['data_pedido'].min().date()} "
        f"a {pedidos['data_pedido'].max().date()}",
        f"impressão digital da base (sha256): {digital_da_base(BASE)}",
        f"regra: treino até {CORTES['treino']}; validação até {CORTES['validação']}; teste depois",
        "",
        f"{'parte':<10} {'pedidos':>7} {'cancelados':>10} {'% cancel':>8}  {'primeiro':<10}  {'último':<10}  ids (sha256)",
    ]
    for nome in PARTES:
        d = pedidos[parte == nome]
        if nome == "teste":
            canc, taxa = "fechado", "fechado"
        else:
            canc = str(int(d["cancelado"].sum()))
            taxa = f"{d['cancelado'].mean() * 100:.1f}%".replace(".", ",")
        linhas.append(f"{nome:<10} {len(d):>7} {canc:>10} {taxa:>8}  {str(d['data_pedido'].min().date()):<10}  "
                      f"{str(d['data_pedido'].max().date()):<10}  {digital_dos_ids(d['id_pedido'])}")
    linhas.append(f"{'total':<10} {len(pedidos):>7}")
    return linhas


def criar():
    pedidos = ler_base()
    parte = pela_regra(pedidos)
    pd.DataFrame({"id_pedido": pedidos["id_pedido"], "parte": parte}).to_csv(ARQUIVO, index=False)
    linhas = manifesto(pedidos, parte)
    MANIFESTO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    print(f"\ngravados: {ARQUIVO} ({len(pedidos)} linhas) e {MANIFESTO}")


def checar(caminho, mostrar=True):
    """Compara um arquivo de partes com a regra e com o manifesto. Retorna True se tudo bate."""
    falar = print if mostrar else (lambda *a, **k: None)
    caminho = Path(caminho)
    if not MANIFESTO.is_file():
        falar(f"não achei {MANIFESTO}. Rode python3 particoes.py antes.")
        return False
    if not caminho.is_file():
        falar(f"não achei {caminho}.")
        return False
    pedidos = ler_base()
    arq = pd.read_csv(caminho)
    if list(arq.columns) != ["id_pedido", "parte"]:
        falar(f"{caminho}: as colunas precisam ser id_pedido,parte; vieram {','.join(arq.columns)}")
        return False
    guardado = MANIFESTO.read_text(encoding="utf-8").splitlines()
    ok = True

    falar(f"arquivo: {caminho.as_posix()}, {len(arq)} linhas")
    base_igual = guardado[1].split(": ", 1)[1] == digital_da_base(BASE)
    falar(f"base igual à do manifesto: {'sim' if base_igual else 'NÃO, a base mudou depois da divisão'}")
    ok &= base_igual

    repetidos = arq["id_pedido"][arq["id_pedido"].duplicated()].unique()
    faltando = sorted(set(pedidos["id_pedido"]) - set(arq["id_pedido"]))
    sobrando = sorted(set(arq["id_pedido"]) - set(pedidos["id_pedido"]))
    estranhas = sorted(set(arq["parte"].astype(str)) - set(PARTES))
    uma_vez = not (len(repetidos) or faltando or sobrando or estranhas)
    falar(f"cada pedido da base aparece uma vez: {'sim' if uma_vez else 'NÃO'}")
    for rotulo, lista in [("repetidos", list(repetidos)), ("faltando", faltando), ("fora da base", sobrando),
                          ("partes com nome estranho", estranhas)]:
        if len(lista):
            falar(f"  {rotulo}: {len(lista)}, por exemplo {', '.join(str(x) for x in lista[:5])}")
    ok &= uma_vez

    regra = pd.DataFrame({"id_pedido": pedidos["id_pedido"], "regra": pela_regra(pedidos),
                          "data": pedidos["data_pedido"].dt.date})
    junto = regra.merge(arq.drop_duplicates("id_pedido"), on="id_pedido", how="left")
    falar(f"\n{'parte':<10} {'pela regra':>10} {'no arquivo':>10}  {'primeiro':<10}  {'último':<10}  ids iguais ao manifesto")
    digitais = {l.split()[0]: l.split()[-1] for l in guardado[5:8]}
    for nome in PARTES:
        d = junto[junto["parte"] == nome]
        datas = (str(d["data"].min()), str(d["data"].max())) if len(d) else ("-", "-")
        igual = len(d) > 0 and digital_dos_ids(d["id_pedido"]) == digitais.get(nome)
        ok &= bool(igual)
        falar(f"{nome:<10} {int((junto['regra'] == nome).sum()):>10} {len(d):>10}  {datas[0]:<10}  {datas[1]:<10}  "
              f"{'sim' if igual else 'não'}")
    fora = junto[junto["parte"].notna() & (junto["parte"] != junto["regra"])]
    falar(f"pedidos fora da parte que a regra manda: {len(fora)}")
    for _, l in fora.head(3).iterrows():
        falar(f"  pedido {l['id_pedido']} ({l['data']}): no arquivo, {l['parte']}; pela regra, {l['regra']}")
    ok &= len(fora) == 0
    falar("resultado: " + ("as partes batem com a regra e com o manifesto" if ok
                           else "as partes não batem; não use esse arquivo"))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--checar", metavar="ARQUIVO", help="arquivo id_pedido,parte para comparar com a regra")
    args = ap.parse_args()
    if args.checar:
        sys.exit(0 if checar(args.checar) else 1)
    criar()
