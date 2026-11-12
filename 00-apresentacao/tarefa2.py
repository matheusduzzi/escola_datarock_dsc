import pandas as pd


def taxa_por_grupo(df, coluna):
    """Retorna uma linha por valor de `coluna`, com as colunas:
    coluna, pedidos, cancelados e taxa_pct (porcentagem com uma casa decimal).
    Valor vazio em `coluna` vira o grupo "sem informação".
    As linhas saem em ordem alfabética do grupo."""
    # Escreva a função aqui e apague a linha abaixo.
    raise NotImplementedError("a função taxa_por_grupo ainda não foi escrita")


if __name__ == "__main__":
    pedidos = pd.read_csv("dados/pedidos_marco.csv")
    print(taxa_por_grupo(pedidos, "forma_pagamento").to_string(index=False))
