"""Modelo de cancelamento da Loja Exemplo. Entrega da consultoria, versão de 20/07/2026.

    python3 consultoria_cancelamento.py

preparar(base) recebe o export completo dos pedidos e retorna x_treino, y_treino, x_teste e
y_teste, com o id do pedido no índice. O modelo é o classificador que a loja já usa
(classificador.py), para a comparação ser justa. O corte é o da loja: 5 / 15.
"""
import sys
from pathlib import Path

import pandas as pd

from classificador import acerto_do_par, nota, pct, treinar

BASE = Path("../dados/loja/pedidos_export_completo.csv")
CORTE = 5 / 15
NUMERICAS = ["valor", "prazo_prometido_dias", "pedidos_anteriores", "cliente_novo"]
CATEGORIAS = ["categoria", "forma_pagamento", "canal"]
FAIXAS_VALOR = [0, 100, 200, 400, float("inf")]


def perfil(b):
    """O perfil do pedido: categoria, pagamento, canal, cliente novo e faixa de valor."""
    faixa = pd.cut(b["valor"], FAIXAS_VALOR, labels=["ate100", "100a200", "200a400", "400mais"])
    return (b["categoria"] + "|" + b["forma_pagamento"] + "|" + b["canal"] + "|"
            + b["cliente_novo"].astype(str) + "|" + faixa.astype(str))


def preparar(base):
    b = base.reset_index(drop=True).copy()

    # Rótulo: cancelado é o pedido que não chegou a ser entregue.
    b["rotulo"] = (b["dias_ate_entrega"] == 0).astype(int)

    # Escala das colunas de número e uma coluna por categoria.
    x = (b[NUMERICAS] - b[NUMERICAS].mean()) / b[NUMERICAS].std(ddof=0)
    for c in CATEGORIAS:
        for v in sorted(b[c].unique()):
            x[f"{c}_{v}"] = (b[c] == v).astype(float)

    # Coluna nova: a taxa de cancelamento do perfil do pedido.
    x["taxa_perfil"] = b.groupby(perfil(b))["rotulo"].transform("mean")

    x.index = b["id_pedido"].to_numpy()
    y = pd.Series(b["rotulo"].to_numpy(), index=x.index)

    # Teste: 30% dos pedidos, sorteados. O sorteio é fixo para dar o mesmo resultado sempre.
    teste = b.sample(frac=0.3, random_state=17)["id_pedido"].to_numpy()
    no_teste = x.index.isin(teste)
    return x[~no_teste], y[~no_teste], x[no_teste], y[no_teste]


def main():
    if not BASE.is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 17-auditoria-de-um-pipeline do kit.")
    x_tr, y_tr, x_te, y_te = preparar(pd.read_csv(BASE, parse_dates=["data_pedido"]))
    s = nota(treinar(x_tr, y_tr), x_te)
    lista = s > CORTE
    certas = int((lista & (y_te == 1)).sum())
    print(f"treino: {len(x_tr)} pedidos; teste: {len(x_te)} pedidos, {int(y_te.sum())} cancelados")
    print(f"lista com corte 0,333: {int(lista.sum())} ligações, {certas} certas")
    print(f"precisão {pct(certas / lista.sum())}, revocação {pct(certas / y_te.sum())}, "
          f"acerto do par {pct(acerto_do_par(s, y_te))}")


if __name__ == "__main__":
    main()
