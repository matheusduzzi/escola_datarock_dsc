"""A preparação do Rafael para o modelo de cancelamento. Ela tem dois vazamentos, de propósito.

Aula «Detectar vazamento» do curso ML: preparação e validação. Não use esse arquivo como modelo:
ele é o caso que a aula desmonta. O certo está em pipeline_corrigido.py.

preparar(base) recebe o export completo dos pedidos, com os 2400 pedidos, e retorna
x_treino, y_treino, x_validacao, y_validacao. Treino: janeiro a março de 2026; validação: abril e
maio. Junho é o teste.
"""
import pandas as pd

FIM_TREINO = "2026-03-31"
FIM_VALIDACAO = "2026-05-31"
NUMERICAS = ["valor", "prazo_prometido_dias", "pedidos_anteriores", "cliente_novo",
             "dias_ate_entrega", "contatos_sac"]          # "o export completo tem mais colunas, pus todas"
CATEGORIAS = ["categoria", "forma_pagamento", "canal"]


def combinacao(p):
    return (p["categoria"] + " " + p["forma_pagamento"] + " " + p["canal"] + " "
            + p["cliente_novo"].astype(str) + " " + p["prazo_prometido_dias"].astype(str))


def preparar(base):
    p = base.copy()
    # tudo calculado com os 2400 pedidos, antes de separar
    x = (p[NUMERICAS] - p[NUMERICAS].mean()) / p[NUMERICAS].std(ddof=0)
    for c in CATEGORIAS:
        for v in sorted(p[c].unique()):
            x[f"{c}_{v}"] = (p[c] == v).astype(float)
    taxa = p.groupby(combinacao(p))["cancelado"].mean()
    x["taxa_combinacao"] = combinacao(p).map(taxa)
    x.index = p["id_pedido"].to_numpy()
    # só agora separa
    data = p["data_pedido"].to_numpy()
    tr = data <= pd.Timestamp(FIM_TREINO)
    va = (data > pd.Timestamp(FIM_TREINO)) & (data <= pd.Timestamp(FIM_VALIDACAO))
    y = pd.Series(p["cancelado"].to_numpy(), index=x.index)
    return x[tr], y[tr], x[va], y[va]
