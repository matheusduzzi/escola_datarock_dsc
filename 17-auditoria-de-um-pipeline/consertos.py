"""Os consertos do modelo da consultoria, um de cada vez e somados.

Aula «Auditoria de um pipeline» do curso ML: preparação e validação.

Cada função tem a mesma entrada e a mesma saída do preparar() da consultoria. A coluna nova
(taxa_perfil), as colunas e o classificador continuam os deles. Só muda o defeito consertado:

- com_alvo:            o rótulo é a coluna cancelado, como no contrato do alvo;
- com_alvo_e_divisao:  mais a divisão por data da aula 05. Treino de janeiro a março, medida em
                       abril e maio. Junho é o teste da aula 16 e sai logo depois da leitura;
- com_tudo:            mais a preparação ajustada só no treino: escala, categorias e taxa do perfil.
                       Perfil que o treino não tem recebe a taxa geral do treino.
"""
import pandas as pd

from consultoria_cancelamento import CATEGORIAS, NUMERICAS, perfil

FIM_TREINO = pd.Timestamp("2026-03-31")
FIM_VALIDACAO = pd.Timestamp("2026-05-31")


def _preparar(base, alvo, divisao, transformacao):
    b = base.reset_index(drop=True).copy()
    b["rotulo"] = b["cancelado"] if alvo else (b["dias_ate_entrega"] == 0).astype(int)

    if divisao:
        b = b[b["data_pedido"] <= FIM_VALIDACAO].reset_index(drop=True)       # junho sai aqui
        no_teste = (b["data_pedido"] > FIM_TREINO).to_numpy()
    else:
        teste = b.sample(frac=0.3, random_state=17)["id_pedido"].to_numpy()
        no_teste = b["id_pedido"].isin(teste).to_numpy()

    ref = b[~no_teste] if transformacao else b                # de onde saem os números
    x = (b[NUMERICAS] - ref[NUMERICAS].mean()) / ref[NUMERICAS].std(ddof=0)
    for c in CATEGORIAS:
        for v in sorted(ref[c].unique()):
            x[f"{c}_{v}"] = (b[c] == v).astype(float)
    if transformacao:
        taxa = ref.groupby(perfil(ref))["rotulo"].mean()
        x["taxa_perfil"] = perfil(b).map(taxa).fillna(ref["rotulo"].mean()).to_numpy()
    else:
        x["taxa_perfil"] = b.groupby(perfil(b))["rotulo"].transform("mean")

    x.index = b["id_pedido"].to_numpy()
    y = pd.Series(b["rotulo"].to_numpy(), index=x.index)
    return x[~no_teste], y[~no_teste], x[no_teste], y[no_teste]


def com_alvo(base):
    return _preparar(base, alvo=True, divisao=False, transformacao=False)


def com_alvo_e_divisao(base):
    return _preparar(base, alvo=True, divisao=True, transformacao=False)


def com_tudo(base):
    return _preparar(base, alvo=True, divisao=True, transformacao=True)
