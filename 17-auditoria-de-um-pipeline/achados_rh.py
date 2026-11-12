"""O exercício da aula «Auditoria de um pipeline»: as três perguntas ao modelo do acompanhamento.

    python3 testar_achados_rh.py      # os testes das suas três funções
    python3 auditar_rh.py achados     # as três perguntas, feitas aos três pipelines

Cada função recebe a base das admissões (como o pandas lê ../dados/pessoas/admissoes.csv, com as
datas já como data) e o que um pipeline retorna. Um pipeline é qualquer função preparar(base) que
retorna x_treino, y_treino, x_medida e y_medida, com o id_pessoa no índice. "Medida" é a parte em
que o pipeline mede o modelo: o teste, para a consultoria; a validação, para o pipeline da aula 09.

O contrato do alvo é o da aula 03: a linha é uma admissão; entra quem ainda estava na loja no dia
7; o rótulo é 1 se a pessoa saiu até 180 dias depois da admissão, contando o dia 180, e 0 se
completou 180 dias sem sair; com a base extraída em 2026-06-30, só entram as admissões até
2026-01-01. As de depois ficam fora, mesmo quem já saiu.

trocar_resultado() e trocar_distancia() estão prontas. Você escreve as três checar_*().
"""
import pandas as pd

from auditoria import linhas_que_mudaram

EXTRACAO = pd.Timestamp("2026-06-30")
HORIZONTE = 180
DIA_DA_LISTA = 7
FIM_CONTRATO = pd.Timestamp("2026-01-01")
INICIO_TESTE = pd.Timestamp("2025-10-01")    # o teste do acompanhamento, aberto uma vez na aula 16


# ---------------------------------------------------------------- pronto

def trocar_resultado(base, ids):
    """Inverte o resultado das pessoas de ids. Quem saiu até o dia 180 passa a ficar; quem ficou,
    ou saiu depois do dia 180, passa a sair no dia 30. saiu_180d acompanha a troca."""
    b = base.copy()
    m = b["id_pessoa"].isin(ids)
    dias = (b["data_desligamento"] - b["data_admissao"]).dt.days
    saiu = m & (dias <= HORIZONTE)
    fica = m & ~(dias <= HORIZONTE)
    completou = b["data_admissao"] + pd.Timedelta(days=HORIZONTE) <= EXTRACAO
    b.loc[saiu, "data_desligamento"] = pd.NaT
    b.loc[saiu, "saiu_180d"] = completou[saiu].map({True: 0.0, False: float("nan")})
    b.loc[fica, "data_desligamento"] = b.loc[fica, "data_admissao"] + pd.Timedelta(days=30)
    b.loc[fica, "saiu_180d"] = 1.0
    return b


def trocar_distancia(base, ids):
    """Põe 90 km de distância para as pessoas de ids."""
    b = base.copy()
    b.loc[b["id_pessoa"].isin(ids), "distancia_km"] = 90.0
    return b


# ---------------------------------------------------------------- as três perguntas

def checar_alvo(base, y):
    """O rótulo que o pipeline deu a cada pessoa contra o contrato do alvo.

    y: a Series de rótulos que o pipeline retorna (treino e medida juntos), com o id_pessoa no índice.
    Retorna um dicionário com:
      saiu_ate_o_dia_7      pessoas de y que saíram até o dia 7: a lista chega tarde para elas
      depois_de_2026_01_01  pessoas de y admitidas depois de 2026-01-01: a turma ainda não tem resposta
      fora_do_contrato      a soma das duas
      rotulo_diferente      pessoas de y que estão no contrato, mas com um rótulo diferente do dele
    """
    raise NotImplementedError("a checar_alvo() ainda não foi escrita")


def checar_divisao(base, ids_treino, ids_medida):
    """As datas de admissão do treino contra as da medida.

    Retorna um dicionário com:
      treino_depois_do_inicio  pessoas do treino admitidas no dia da primeira admissão da medida
                               ou depois
      teste_no_treino          pessoas do treino admitidas de 2025-10-01 a 2026-01-01: o teste do
                               acompanhamento, que a aula 16 abriu uma vez
    """
    raise NotImplementedError("a checar_divisao() ainda não foi escrita")


def checar_transformacao(base, preparar):
    """Mexe só nas pessoas da medida e vê o que muda na tabela que o modelo recebe.

    preparar: a função do pipeline. Rode uma vez com a base, ache as pessoas da medida e rode de
    novo duas vezes: com trocar_resultado() e com trocar_distancia() nessas pessoas.
    Retorna um dicionário com:
      treino_com_resultado  linhas de x_treino que mudam quando o resultado da medida muda
      medida_com_resultado  linhas de x_medida que mudam quando o resultado dela mesma muda
      treino_com_distancia  linhas de x_treino que mudam quando a distância da medida muda
    Use linhas_que_mudaram(antes, depois), do auditoria.py, para contar.
    """
    raise NotImplementedError("a checar_transformacao() ainda não foi escrita")
