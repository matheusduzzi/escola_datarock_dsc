"""A auditoria da lista de acompanhamento por loja, cargo e turno.

Aula «Auditar estabilidade por segmento» do curso ML: preparação e validação.
Rode de dentro da pasta da aula:

    python3 auditar.py                    # o relatório da aula
    python3 auditar.py --colunas turno    # o embaralhamento só com os recortes de turno

A parte que prepara é a das aulas 09 e 11: treino com as admitidas até 30/06/2025, validação com
as admitidas de julho a setembro de 2025, o pipeline das admissões e o classificador pronto. O
teste fica fechado. A regra acompanha quem passa do empate, 32%.

O relatório tem três blocos:
1. quem cada recorte cobre: pessoas no treino, na validação e entre as pessoas novas;
2. a lista em cada recorte, com a faixa de 1000 sorteios com reposição;
3. o melhor e o pior recorte quando as notas são embaralhadas.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ACOMPANHAMENTO = 240      # R$ de um acompanhamento
SAIDA = 3000              # R$ de uma saída antes de 180 dias
EFEITO = 0.25             # o acompanhamento evita 1 de cada 4 saídas de quem ia sair
EMPATE = ACOMPANHAMENTO / (EFEITO * SAIDA)    # 0,32
COLUNAS = ["loja", "cargo", "turno"]
PASTA = "15-auditar-estabilidade-por-segmento"


def carregar():
    """Treino, validação com nota e pessoas novas com nota. O teste sai no separar() e não volta."""
    if not Path("pipeline_pessoas.py").is_file() or not Path("../dados/pessoas/admissoes.csv").is_file():
        sys.exit(f"não achei os arquivos. Rode de dentro da pasta {PASTA} do kit.")
    import classificador
    import pipeline_pessoas as pp
    treino, validacao, _, novas = pp.separar(pp.carregar())
    params = pp.ajustar(treino)
    x_tr = pp.aplicar(params, treino)
    x_va = pp.aplicar(params, validacao)
    y_tr = treino.set_index("id_pessoa").loc[x_tr.index, "saiu_180d"]
    modelo = classificador.treinar(x_tr[params["colunas"]], y_tr)
    v = validacao.set_index("id_pessoa").loc[x_va.index, COLUNAS].copy()
    v["saiu_180d"] = validacao.set_index("id_pessoa").loc[x_va.index, "saiu_180d"].astype(int)
    v["nota"] = classificador.nota(modelo, x_va[params["colunas"]])
    x_nv = pp.aplicar(params, novas)
    novas = novas.set_index("id_pessoa").loc[x_nv.index, COLUNAS].copy()
    novas["liberada"] = x_nv["liberada"]
    novas["nota"] = classificador.nota(modelo, x_nv[params["colunas"]].fillna(0))
    return treino, v, novas


def saldo(y, nota):
    """Em reais, contra não acompanhar ninguém: saídas evitadas menos acompanhamentos."""
    marcar = np.asarray(nota) > EMPATE
    acertos = int((marcar & (np.asarray(y) == 1)).sum())
    return acertos * EFEITO * SAIDA - int(marcar.sum()) * ACOMPANHAMENTO


def acerto_par(y, nota):
    import classificador
    y = np.asarray(y)
    if y.sum() == 0 or y.sum() == len(y):
        return None
    return classificador.acerto_do_par(nota, y)


def recortes(treino, v, novas, colunas=COLUNAS):
    """Todos os valores de cada coluna, os do treino, os da validação e os das pessoas novas."""
    lista = []
    for c in colunas:
        for valor in sorted(set(treino[c]) | set(v[c]) | set(novas[c])):
            lista.append((c, valor))
    return lista


def linha(v, coluna, valor):
    import segmentos
    r = v[v[coluna] == valor]
    y, nota = r["saiu_180d"].to_numpy(), r["nota"].to_numpy()
    marcar = nota > EMPATE
    s_baixo, s_alto, _ = segmentos.faixa(saldo, [y, nota])
    p_baixo, p_alto, _ = segmentos.faixa(acerto_par, [y, nota])
    return {"pessoas": len(r), "saidas": int(y.sum()), "acompanhadas": int(marcar.sum()),
            "acertos": int((marcar & (y == 1)).sum()), "saldo": saldo(y, nota) if len(r) else None,
            "faixa_saldo": (s_baixo, s_alto), "acerto_par": acerto_par(y, nota) if len(r) else None,
            "faixa_par": (p_baixo, p_alto), "leitura": segmentos.leitura(s_baixo, s_alto)}


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    if x is None:
        return "-"
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def de_a(par, f):
    return "-" if par[0] is None else f"{f(par[0])} a {f(par[1])}"


def main():
    ap = argparse.ArgumentParser(description="auditoria da lista de acompanhamento por recorte")
    ap.add_argument("--colunas", nargs="+", choices=COLUNAS, default=COLUNAS,
                    help="as colunas que entram no embaralhamento do bloco 3")
    args = ap.parse_args()
    import segmentos

    treino, v, novas = carregar()
    y, nota = v["saiu_180d"].to_numpy(), v["nota"].to_numpy()
    print(f"validação: {len(v)} pessoas admitidas de julho a setembro de 2025, {int(y.sum())} saíram antes de "
          f"180 dias ({pct(y.mean())}); o teste fica fechado")
    print(f"regra: acompanha quem passa do empate, {pct(EMPATE)}; acompanhamento R$ {ACOMPANHAMENTO}, saída "
          f"R$ {num(SAIDA, 0)}, evita 1 de cada 4")
    g = linha(v.assign(todas="todas"), "todas", "todas")
    print(f"todas as pessoas: {g['acompanhadas']} acompanhadas, {g['acertos']} iam sair, saldo {reais(g['saldo'])}, "
          f"faixa {de_a(g['faixa_saldo'], reais)}; acerto do par {pct(g['acerto_par'])}, "
          f"faixa {de_a(g['faixa_par'], pct)}")
    print(f"faixas: {segmentos.SORTEIOS} sorteios com reposição dentro de cada recorte, sorteio {segmentos.SORTEIO}; "
          f"tira 2,5% de cada lado")

    lista = recortes(treino, v, novas)
    print("\n1. quem cada recorte cobre")
    print(f"{'recorte':<27}{'treino':>7}{'saíram':>8}{'validação':>10}{'saíram':>8}{'pessoas novas':>14}")
    sem_medida = pd.Series(False, index=novas.index)
    for c, valor in lista:
        t = treino[treino[c] == valor]
        r = v[v[c] == valor]
        nn = int((novas[c] == valor).sum())
        if len(r) == 0:
            sem_medida |= novas[c] == valor
        print(f"{c + ' ' + valor:<27}{len(t):>7}{pct(t['saiu_180d'].mean() if len(t) else None):>8}"
              f"{len(r):>10}{pct(r['saiu_180d'].mean() if len(r) else None):>8}{nn:>14}")
    print(f"   pessoas novas, admitidas depois de 01/01/2026: {len(novas)}; num recorte sem ninguém na validação: "
          f"{int(sem_medida.sum())} ({pct(sem_medida.mean())})")
    fora = novas[sem_medida & novas["liberada"]]
    print(f"   a lista dá nota para {len(fora)} delas e acompanharia {int((fora['nota'] > EMPATE).sum())}; "
          f"na validação, ela acompanhou {pct((nota > EMPATE).mean())} das pessoas")

    print("\n2. a lista em cada recorte")
    print(f"{'recorte':<27}{'pessoas':>8}{'saíram':>7}{'acomp.':>7}{'acertos':>8}{'saldo':>11}"
          f"{'faixa do saldo':>24}{'par':>7}{'faixa do par':>17}  leitura")
    medidos = []
    for c, valor in lista:
        r = linha(v, c, valor)
        if r["pessoas"]:
            medidos.append((c, valor, r))
        print(f"{c + ' ' + valor:<27}{r['pessoas']:>8}{r['saidas']:>7}{r['acompanhadas']:>7}{r['acertos']:>8}"
              f"{reais(r['saldo']):>11}{de_a(r['faixa_saldo'], reais):>24}{pct(r['acerto_par']):>7}"
              f"{de_a(r['faixa_par'], pct):>17}  {r['leitura']}")
    leituras = pd.Series([r["leitura"] for _, _, r in medidos]).value_counts()
    print("   " + "; ".join(f"{k}: {n}" for k, n in leituras.items()))

    escolhidos = [(c, valor, r) for c, valor, r in medidos if c in args.colunas]
    mascaras = [(v[c] == valor).to_numpy() for c, valor, _ in escolhidos]
    melhor = max(escolhidos, key=lambda t: t[2]["saldo"])
    pior = min(escolhidos, key=lambda t: t[2]["saldo"])
    melhores, piores = segmentos.embaralhar(nota, mascaras, lambda n, m: saldo(y[m], n))
    melhores, piores = np.asarray(melhores), np.asarray(piores)
    print(f"\n3. as notas embaralhadas entre as {len(v)} pessoas, {segmentos.SORTEIOS} vezes, "
          f"nos {len(escolhidos)} recortes de {', '.join(args.colunas)}")
    print(f"   o melhor recorte de verdade: {melhor[0]} {melhor[1]}, {reais(melhor[2]['saldo'])}; "
          f"o pior: {pior[0]} {pior[1]}, {reais(pior[2]['saldo'])}")
    print(f"   melhor recorte com as notas embaralhadas: mediana {reais(float(np.median(melhores)))}; "
          f"acima de zero em {pct((melhores > 0).mean())} das vezes; chega a {reais(melhor[2]['saldo'])} "
          f"em {pct((melhores >= melhor[2]['saldo']).mean())}")
    print(f"   pior recorte com as notas embaralhadas: mediana {reais(float(np.median(piores)))}; "
          f"chega a {reais(pior[2]['saldo'])} em {pct((piores <= pior[2]['saldo']).mean())}")


if __name__ == "__main__":
    main()
