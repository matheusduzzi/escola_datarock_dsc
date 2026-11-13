"""Quanto custa cada regra de ligação, com o preço que você der para cada erro.

Rode de dentro da pasta da aula:
    python3 custo_das_regras.py
    python3 custo_das_regras.py --cancelamento 30

Uma ligação custa sempre o preço de --ligacao, acerte ou não.
Um cancelamento que passa sem ligação custa o preço de --cancelamento.
Quando a equipe liga para um pedido que ia cancelar, o cancelamento acontece
antes da separação e a loja não paga esse preço.
"""
import argparse

import pandas as pd

ARQUIVO = "../dados/loja/pedidos.csv"


def positivo(texto):
    valor = float(texto)
    if valor <= 0:
        raise argparse.ArgumentTypeError(f"precisa ser maior que zero, veio {texto}")
    return valor


def reais(valor):
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


def pct(parte, todo):
    if todo == 0:
        return "-"
    return f"{100 * parte / todo:.1f}%".replace(".", ",")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--ligacao", type=positivo, default=5, help="preço de uma ligação, em reais")
    p.add_argument("--cancelamento", type=positivo, default=15,
                   help="preço de um cancelamento que passa sem ligação, em reais")
    p.add_argument("--capacidade", type=int, default=600,
                   help="ligações que a equipe dá conta no semestre")
    a = p.parse_args()

    pedidos = pd.read_csv(ARQUIVO)
    cancela = pedidos["cancelado"] == 1
    total, cancelados = len(pedidos), int(cancela.sum())
    regras = {
        "nunca liga": pd.Series(False, index=pedidos.index),
        "liga para todos": pd.Series(True, index=pedidos.index),
        "boleto": pedidos["forma_pagamento"] == "boleto",
        "cliente novo": pedidos["cliente_novo"] == 1,
    }

    print(f"{total} pedidos, {cancelados} cancelados ({pct(cancelados, total)})")
    print(f"preços: ligação {reais(a.ligacao)}, cancelamento sem ligação {reais(a.cancelamento)}")
    print(f"capacidade da equipe: {a.capacidade} ligações")
    print(f"a ligação se paga quando mais de {pct(a.ligacao, a.cancelamento)} das ligações vão "
          "para quem ia cancelar")
    print()
    print(f"{'regra':<16}{'ligações':>9}{'certas':>8}{'passam':>8}{'precisão':>10}"
          f"{'revocação':>11}{'custo':>11}  cabe?")
    for nome, liga in regras.items():
        ligacoes = int(liga.sum())
        certas = int((liga & cancela).sum())
        passam = cancelados - certas
        custo = a.ligacao * ligacoes + a.cancelamento * passam
        cabe = "sim" if ligacoes <= a.capacidade else "não"
        print(f"{nome:<16}{ligacoes:>9}{certas:>8}{passam:>8}{pct(certas, ligacoes):>10}"
              f"{pct(certas, cancelados):>11}{reais(custo):>11}  {cabe}")


if __name__ == "__main__":
    main()
