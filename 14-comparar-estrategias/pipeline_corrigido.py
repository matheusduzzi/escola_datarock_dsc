"""A preparação do modelo de cancelamento sem os dois vazamentos.

Aula «Detectar vazamento» do curso ML: preparação e validação.

preparar(base) recebe o export completo dos pedidos e retorna x_treino, y_treino, x_validacao,
y_validacao, como a do Rafael. A diferença está em duas coisas:

- só entram colunas que existem na hora do pedido; dias_ate_entrega e contatos_sac ficam fora;
- separa primeiro e ajusta depois: média, desvio e categorias saem só do treino (janeiro a março).
  Junho, o teste, sai logo depois da leitura e não entra em nenhuma conta.
"""
import pandas as pd

FIM_TREINO = "2026-03-31"
FIM_VALIDACAO = "2026-05-31"
NUMERICAS = ["valor", "prazo_prometido_dias", "pedidos_anteriores", "cliente_novo"]
CATEGORIAS = ["categoria", "forma_pagamento", "canal"]
NASCEM_DEPOIS = ["dias_ate_entrega", "contatos_sac"]       # gravadas depois do pedido


def ajustar(treino):
    if (treino["data_pedido"] > pd.Timestamp(FIM_TREINO)).any():
        raise ValueError(f"ajustar só recebe o treino, até {FIM_TREINO}")
    return {"media": treino[NUMERICAS].mean(), "desvio": treino[NUMERICAS].std(ddof=0),
            "categorias": {c: sorted(treino[c].unique()) for c in CATEGORIAS}}


def aplicar(params, pedidos):
    x = (pedidos[NUMERICAS] - params["media"]) / params["desvio"]
    for c in CATEGORIAS:
        for v in params["categorias"][c]:
            x[f"{c}_{v}"] = (pedidos[c] == v).astype(float)
    x.index = pedidos["id_pedido"].to_numpy()
    return x


def preparar(base):
    p = base[base["data_pedido"] <= pd.Timestamp(FIM_VALIDACAO)]      # junho sai aqui
    treino = p[p["data_pedido"] <= pd.Timestamp(FIM_TREINO)]
    validacao = p[p["data_pedido"] > pd.Timestamp(FIM_TREINO)]
    params = ajustar(treino)
    y_tr = pd.Series(treino["cancelado"].to_numpy(), index=treino["id_pedido"].to_numpy())
    y_va = pd.Series(validacao["cancelado"].to_numpy(), index=validacao["id_pedido"].to_numpy())
    return aplicar(params, treino), y_tr, aplicar(params, validacao), y_va
