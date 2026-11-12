"""O exercício da aula «Auditoria de um pipeline»: o modelo da consultoria com os três consertos.

    python3 auditar_rh.py consertos

preparar(base) tem a mesma entrada e a mesma saída do preparar() de consultoria_acompanhamento.py.
Comece por uma cópia do preparar() deles. As colunas continuam as deles, inclusive a taxa_equipe,
e o classificador é o mesmo. O que muda é cada defeito que as suas checar_*() acharam.

A medida é a validação da aula 09: treino com as admissões até 2025-06-30, medida nas de julho a
setembro de 2025. O teste do acompanhamento já foi aberto na aula 16 e não entra.
"""
import pandas as pd

from consultoria_acompanhamento import CATEGORIAS, NUMERICAS  # noqa: F401

EXTRACAO = pd.Timestamp("2026-06-30")
FIM_TREINO = pd.Timestamp("2025-06-30")
FIM_VALIDACAO = pd.Timestamp("2025-09-30")


def preparar(base):
    """Retorna x_treino, y_treino, x_medida e y_medida, com o id_pessoa no índice."""
    raise NotImplementedError("o preparar() de consertar_rh.py ainda não foi escrito")
