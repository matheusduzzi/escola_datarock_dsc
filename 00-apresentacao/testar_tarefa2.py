"""Testes da tarefa 2. Rode com: python3 testar_tarefa2.py"""
import pandas as pd

from tarefa2 import taxa_por_grupo


def testar_caso_pequeno():
    df = pd.DataFrame({"canal": ["app", "site", "app", None], "cancelado": [1, 0, 0, 1]})
    r = taxa_por_grupo(df, "canal")
    assert list(r.columns) == ["canal", "pedidos", "cancelados", "taxa_pct"], list(r.columns)
    assert list(r["canal"]) == ["app", "sem informação", "site"], list(r["canal"])
    assert list(r["pedidos"]) == [2, 1, 1], list(r["pedidos"])
    assert list(r["taxa_pct"]) == [50.0, 100.0, 0.0], list(r["taxa_pct"])


def testar_nenhum_pedido_some():
    df = pd.read_csv("dados/pedidos_marco.csv")
    r = taxa_por_grupo(df, "forma_pagamento")
    assert r["pedidos"].sum() == len(df), "a soma de pedidos não bate com o total de linhas"
    assert r["cancelados"].sum() == df["cancelado"].sum(), "a soma de cancelados não bate"
    conta = (100 * r["cancelados"] / r["pedidos"]).round(1)
    assert (conta == r["taxa_pct"]).all(), "taxa_pct não é cancelados / pedidos"
    assert not df["forma_pagamento"].fillna("x").eq("sem informação").any(), "a função mudou o df de entrada"


if __name__ == "__main__":
    testar_caso_pequeno()
    testar_nenhum_pedido_some()
    print("os dois testes passaram")
