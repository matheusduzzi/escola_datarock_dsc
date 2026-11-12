"""Onde está a resposta? Conta, nas duas bases do kit, quantas linhas já têm a resposta preenchida.

Rode de dentro da pasta 02-tipos-de-aprendizado:  python3 onde_esta_a_resposta.py
"""
import pandas as pd

pedidos = pd.read_csv("../dados/loja/pedidos.csv")
admissoes = pd.read_csv("../dados/pessoas/admissoes.csv")

for nome, base, coluna in [("pedidos", pedidos, "cancelado"), ("admissões", admissoes, "saiu_180d")]:
    tem = int(base[coluna].notna().sum())
    vazio = int(base[coluna].isna().sum())
    print(f"{nome}: {len(base)} linhas; resposta ({coluna}) preenchida em {tem}, vazia em {vazio}")

sem = admissoes[admissoes["saiu_180d"].isna()]
print(f"admissões sem resposta: contratadas de {sem['data_admissao'].min()} a {sem['data_admissao'].max()}")

recentes = admissoes[admissoes["data_admissao"] >= "2026-01-01"]
com = recentes.dropna(subset=["saiu_180d"])
print(f"contratadas em 2026: {len(recentes)}; com resposta: {len(com)}, das quais {int(com['saiu_180d'].sum())} saíram")
