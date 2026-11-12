"""Abre o teste uma vez e aplica a régua. Aula «Decidir pelo critério» do curso ML: preparação e validação.

    python3 decidir.py                                     # mostra o plano; o teste continua fechado
    python3 decidir.py --abrir                             # abre junho, aplica a régua e anota a abertura
    python3 decidir.py --abrir                             # de novo: refaz a conta e compara com a anotação
    python3 decidir.py --abrir --regua regua-do-rafael.json   # outro plano depois da abertura: recusa

O plano fica em regua.json: preços, classificador, corte e as quatro condições do briefing da aula 01.
Sem --abrir, o programa só lê o plano: nenhum pedido é lido.
Com --abrir, ele prepara e treina como nas aulas 10 e 11 (janeiro a março), dá a nota dos pedidos de
junho, mede três regras nos mesmos pedidos e aplica a régua. A primeira abertura grava abertura.json
com o plano e o resultado. Nas seguintes, um plano diferente do anotado é recusado com código 1.
O arquivo não impede ninguém de apagá-lo; ele deixa a abertura à vista de quem lê o projeto depois.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

BASE = Path("../dados/loja/pedidos_export_completo.csv")
REGUA = Path("regua.json")
ABERTURA = Path("abertura.json")
INICIO_TESTE = "2026-06-01"
FIM_TESTE = "2026-06-30"
CAMPOS = ["modelo", "escrito_em", "de_onde_vem", "precos", "classificador", "corte", "teste", "regua"]


def ler_plano(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        sys.exit(f"não achei {caminho}. Rode de dentro da pasta 16-decidir-pelo-criterio do kit.")
    plano = json.loads(caminho.read_text(encoding="utf-8"))
    faltam = [c for c in CAMPOS if c not in plano]
    if faltam:
        sys.exit(f"{caminho}: o plano não tem {', '.join(faltam)}")
    return plano


def impressao(objeto):
    """Os 12 primeiros caracteres do SHA-256 do conteúdo, com as chaves em ordem."""
    texto = json.dumps(objeto, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def _folhas(d, prefixo=""):
    for chave, valor in d.items():
        if isinstance(valor, dict):
            yield from _folhas(valor, f"{prefixo}{chave}.")
        else:
            yield f"{prefixo}{chave}", valor


def diferencas(antes, agora):
    """Cada campo que mudou entre dois planos, no formato 'campo: antes X, agora Y'."""
    a, b = dict(_folhas(antes)), dict(_folhas(agora))
    saida = []
    for campo in sorted(set(a) | set(b)):
        if a.get(campo, "(vazio)") != b.get(campo, "(vazio)"):
            saida.append(f"{campo}: antes {a.get(campo, '(vazio)')}, agora {b.get(campo, '(vazio)')}")
    return saida


def corte_de(plano):
    if plano["corte"] == "empate":
        return plano["precos"]["ligacao"] / plano["precos"]["cancelamento"]
    return float(plano["corte"])


def medir(y, ligar, ligacao, cancelamento):
    """VP, FP, FN, VN, ligações, precisão (None se ninguém recebe ligação), revocação e custo."""
    vp = int((ligar & (y == 1)).sum())
    fp = int((ligar & (y == 0)).sum())
    fn = int((~ligar & (y == 1)).sum())
    vn = int((~ligar & (y == 0)).sum())
    lig = vp + fp
    return {"vp": vp, "fp": fp, "fn": fn, "vn": vn, "ligacoes": lig,
            "precisao": vp / lig if lig else None,
            "revocacao": vp / (vp + fn) if vp + fn else None,
            "custo": ligacao * lig + cancelamento * fn}


def aplicar_regua(lista, boleto, pedidos, regua):
    """As quatro condições do briefing, cada uma com o valor medido e se passa. 'uso' só se todas passam."""
    p, r = lista["precisao"], lista["revocacao"]
    teto = int(pedidos * regua["teto_ligacoes"])
    condicoes = [
        (f"precisão de pelo menos {pct(regua['precisao_minima'], 0)}", pct(p),
         p is not None and p >= regua["precisao_minima"]),
        (f"revocação de pelo menos {pct(regua['revocacao_minima'], 0)}", pct(r),
         r is not None and r >= regua["revocacao_minima"]),
        ("custo menor que o da regra do boleto", f"{reais(lista['custo'])} contra {reais(boleto['custo'])}",
         lista["custo"] < boleto["custo"]),
        ("no máximo 1 ligação para cada 4 pedidos", f"{lista['ligacoes']} de {pedidos}, teto {teto}",
         lista["ligacoes"] <= teto),
    ]
    return condicoes, "uso" if all(c[2] for c in condicoes) else "não uso"


def abrir(plano):
    """Treina como nas aulas 10 e 11 e mede as três regras nos pedidos de junho."""
    if not BASE.is_file() or not Path("classificador.py").is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 16-decidir-pelo-criterio do kit.")
    import numpy as np
    import pandas as pd
    import classificador
    import pipeline_corrigido as prep
    base = pd.read_csv(BASE, parse_dates=["data_pedido"])
    treino = base[base["data_pedido"] <= pd.Timestamp(prep.FIM_TREINO)]
    teste = base[(base["data_pedido"] >= pd.Timestamp(INICIO_TESTE)) & (base["data_pedido"] <= pd.Timestamp(FIM_TESTE))]
    params = prep.ajustar(treino)
    modelo = classificador.treinar(prep.aplicar(params, treino), treino["cancelado"].to_numpy())
    nota = classificador.nota(modelo, prep.aplicar(params, teste)).to_numpy()
    y = teste["cancelado"].to_numpy()
    lig, canc = plano["precos"]["ligacao"], plano["precos"]["cancelamento"]
    corte = corte_de(plano)
    regras = {"nunca liga": np.zeros(len(y), dtype=bool),
              "boleto": (teste["forma_pagamento"] == "boleto").to_numpy(),
              f"classificador, corte {num(corte, 3)}": nota > corte}
    return {"dados": hashlib.sha256(BASE.read_bytes()).hexdigest(),
            "treino": len(treino), "pedidos": len(y), "cancelados": int(y.sum()),
            "regras": {nome: medir(y, ligar, lig, canc) for nome, ligar in regras.items()}}


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x, casas=1):
    return "-" if x is None else num(100 * x, casas) + "%"


def reais(x):
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def relatorio(plano, resultado):
    n = resultado["pedidos"]
    print(f"teste: {n} pedidos de junho de 2026, {resultado['cancelados']} cancelados "
          f"({pct(resultado['cancelados'] / n)})")
    print(f"classificador ajustado nos {resultado['treino']} pedidos de janeiro a março\n")
    print(f"{'regra':<28} {'VP':>4} {'FP':>4} {'FN':>4} {'VN':>4} {'ligações':>9} {'precisão':>9} "
          f"{'revocação':>10} {'custo':>9}")
    for nome, m in resultado["regras"].items():
        print(f"{nome:<28} {m['vp']:>4} {m['fp']:>4} {m['fn']:>4} {m['vn']:>4} {m['ligacoes']:>9} "
              f"{pct(m['precisao']):>9} {pct(m['revocacao']):>10} {reais(m['custo']):>9}")
    nome_lista = [k for k in resultado["regras"] if k.startswith("classificador")][0]
    condicoes, decisao = aplicar_regua(resultado["regras"][nome_lista], resultado["regras"]["boleto"], n,
                                       plano["regua"])
    print(f"\na régua de {plano['escrito_em']}, aplicada à lista do {nome_lista}")
    for texto, valor, passa in condicoes:
        print(f"  {texto:<42} {valor:<24} {'passa' if passa else 'não passa'}")
    print(f"\ndecisão pela régua: {decisao}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--regua", default=str(REGUA), help="o arquivo do plano (padrão: regua.json)")
    ap.add_argument("--abrir", action="store_true", help="abre o teste e aplica a régua")
    args = ap.parse_args()
    plano = ler_plano(args.regua)
    print(f"plano: {args.regua}, escrito em {plano['escrito_em']}, impressão digital {impressao(plano)}")
    print(f"corte: {plano['corte']} ({num(corte_de(plano), 3)}); preços: ligação R$ {plano['precos']['ligacao']}, "
          f"cancelamento R$ {plano['precos']['cancelamento']}")

    if not args.abrir:
        print("teste: fechado. Nenhum pedido foi lido. Para abrir, uma vez: python3 decidir.py --abrir")
        return

    if ABERTURA.is_file():
        anotada = json.loads(ABERTURA.read_text(encoding="utf-8"))
        mudou = diferencas(anotada["plano"], plano)
        if mudou:
            print(f"\nrecusado: o teste já foi aberto com o plano {impressao(anotada['plano'])}, e esse é outro.",
                  file=sys.stderr)
            for linha in mudou:
                print(f"  {linha}", file=sys.stderr)
            print("um plano novo pede um teste que ainda não foi aberto. O resultado de junho continua o anotado.",
                  file=sys.stderr)
            sys.exit(1)
        resultado = abrir(plano)
        if resultado != anotada["resultado"]:
            print("\nrecusado: com o mesmo plano, a conta de agora não bate com a anotada em abertura.json. "
                  "Os pedidos ou o código mudaram depois da abertura.", file=sys.stderr)
            sys.exit(1)
        print(f"\no teste já foi aberto com esse plano. A conta de agora é igual à anotada em {ABERTURA}.")
        relatorio(plano, resultado)
        return

    resultado = abrir(plano)
    ABERTURA.write_text(json.dumps({"plano": plano, "resultado": resultado}, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"\nteste aberto agora. Plano e resultado anotados em {ABERTURA}.")
    relatorio(plano, resultado)


if __name__ == "__main__":
    main()
