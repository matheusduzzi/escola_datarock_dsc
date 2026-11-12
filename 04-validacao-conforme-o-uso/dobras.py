"""Aula «Validação conforme o uso»: a mesma regra testada por seis jeitos de separar a base.

A base é a das admissões, com as linhas do contrato da aula 03: quem entrou até 01/01/2026 e
ainda estava na loja no dia 7. A regra testada é simples de propósito: a taxa de saída de cada
cargo no treino. Cargo que não aparece no treino recebe a taxa geral do treino.

Em cada parte de teste, o programa soma as taxas previstas (quantas saídas a regra espera) e
compara com quantas pessoas saíram de verdade.

Rode de dentro da pasta da aula:
    python3 dobras.py
    python3 dobras.py --dobras 10
    python3 dobras.py --sem-intervalo
"""
import argparse

import numpy as np
import pandas as pd

BASE = "../dados/pessoas/admissoes.csv"
EXTRACAO = pd.Timestamp("2026-06-30")
HORIZONTE = 180
DIA_DA_LISTA = 7
SORTEIO = 2026  # sorteio fixo: a saída é a mesma toda vez


def numero(x, casas=1):
    texto = f"{x:.{casas}f}"
    if float(texto) == 0:
        texto = f"{0:.{casas}f}"
    return texto.replace(".", ",")


def pct(x):
    return numero(100 * x) + "%"


def carregar():
    a = pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])
    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    madura = a["data_admissao"] <= EXTRACAO - pd.Timedelta(days=HORIZONTE)
    na_lista = ~(dias <= DIA_DA_LISTA)
    p = a[madura & na_lista].copy()
    p["y"] = p["saiu_180d"].astype(int)
    p = p.sort_values(["data_admissao", "id_pessoa"]).reset_index(drop=True)
    return p


def regra(treino, teste):
    """Taxa do cargo no treino; cargo novo recebe a taxa geral do treino."""
    taxa = treino.groupby("cargo")["y"].mean()
    previsto = teste["cargo"].map(taxa).fillna(treino["y"].mean())
    novos = int((~teste["cargo"].isin(taxa.index)).sum())
    return previsto.sum(), int(teste["y"].sum()), novos


def linha(nome, treino, teste):
    previu, sairam, novos = regra(treino, teste)
    extra = f"   cargo sem histórico no treino: {novos}" if novos else ""
    print(f"  {nome:<14}{len(treino):>7}{len(teste):>7}{numero(previu):>8}{sairam:>8}"
          f"{numero(previu - sairam):>8}   {pct(teste['y'].mean())}{extra}")
    return previu - sairam


def cabecalho():
    print(f"  {'teste':<14}{'treino':>7}{'teste':>7}{'previu':>8}{'saíram':>8}{'dif.':>8}   % saíram no teste")


def resumo(difs):
    maior = max(difs, key=abs)
    print(f"  maior diferença numa parte: {numero(maior)}\n")


def dobras_aleatorias(p, k, ordem):
    dobra = np.empty(len(p), dtype=int)
    dobra[ordem] = np.arange(len(p)) % k
    return dobra


def dobras_estratificadas(p, k, ordem):
    dobra = np.empty(len(p), dtype=int)
    for classe in (0, 1):
        idx = ordem[p["y"].to_numpy()[ordem] == classe]
        dobra[idx] = np.arange(len(idx)) % k
    return dobra


def main():
    ap = argparse.ArgumentParser(description="A mesma regra testada por seis jeitos de separar a base.")
    ap.add_argument("--dobras", type=int, default=5, help="número de dobras do k-fold (de 2 a 50)")
    ap.add_argument("--sem-intervalo", action="store_true",
                    help="na separação por tempo, treina com tudo o que veio antes do trimestre de teste")
    args = ap.parse_args()
    if not 2 <= args.dobras <= 50:
        ap.error("--dobras precisa ficar entre 2 e 50")

    p = carregar()
    k = args.dobras
    ordem = np.random.default_rng(SORTEIO).permutation(len(p))
    print(f"admissões do contrato da aula 03: {len(p)} pessoas, {int(p['y'].sum())} saíram ({pct(p['y'].mean())})")
    print("regra testada: a taxa de saída do cargo no treino")
    print("previu = saídas que a regra espera no teste; dif. = previu menos saíram\n")

    print("1. holdout aleatório: 20% sorteados para teste")
    cabecalho()
    n_teste = round(0.2 * len(p))
    teste = p.iloc[ordem[:n_teste]]
    treino = p.iloc[ordem[n_teste:]]
    resumo([linha("sorteio", treino, teste)])

    print(f"2. k-fold aleatório: {k} dobras sorteadas")
    cabecalho()
    dobra = dobras_aleatorias(p, k, ordem)
    resumo([linha(f"dobra {i + 1}", p[dobra != i], p[dobra == i]) for i in range(k)])

    print(f"3. k-fold estratificado: {k} dobras com a mesma proporção de saídas")
    cabecalho()
    dobra = dobras_estratificadas(p, k, ordem)
    resumo([linha(f"dobra {i + 1}", p[dobra != i], p[dobra == i]) for i in range(k)])

    print("4. por grupo: uma loja fica fora do treino e vira o teste")
    cabecalho()
    difs = []
    for loja in sorted(p["loja"].unique()):
        teste = p[p["loja"] == loja]
        if len(teste) < 30:
            print(f"  {loja:<14}{'':>7}{len(teste):>7}   poucas pessoas com resposta: não dá para medir")
            continue
        difs.append(linha(loja, p[p["loja"] != loja], teste))
    resumo(difs)

    tri = p["data_admissao"].dt.to_period("Q")
    if args.sem_intervalo:
        print("5. por tempo: treina com tudo o que veio antes do trimestre, sem intervalo")
    else:
        print(f"5. por tempo: treina só com quem já tinha resposta no início do trimestre ({HORIZONTE} dias antes)")
    cabecalho()
    difs = []
    for q in ["2025Q2", "2025Q3", "2025Q4"]:
        q = pd.Period(q, freq="Q")
        inicio = q.start_time
        teste = p[tri == q]
        if args.sem_intervalo:
            treino = p[tri < q]
        else:
            treino = p[p["data_admissao"] <= inicio - pd.Timedelta(days=HORIZONTE)]
        difs.append(linha(f"{q.year}-T{q.quarter}", treino, teste))
    resumo(difs)

    print("6. leave-one-out: cada pessoa é o teste uma vez")
    y = p["y"].to_numpy()
    soma = p.groupby("cargo")["y"].transform("sum").to_numpy()
    conta = p.groupby("cargo")["y"].transform("size").to_numpy()
    previsto = (soma - y) / (conta - 1)
    print(f"  treinos: {len(p)}; previu {numero(previsto.sum())}, saíram {int(y.sum())}")
    print("  cada teste tem uma pessoa: ela saiu ou não, e a regra deu uma taxa entre 0 e 1")


if __name__ == "__main__":
    main()
