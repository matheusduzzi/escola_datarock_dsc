"""O pipeline do cancelamento: a sua versão. Exercício da aula «Pipeline para dados de pessoas».

Escreva ajustar() e aplicar(). O resto já está pronto. Rode, de dentro da pasta da aula:

    python3 testar_meu_pipeline.py    # os testes do exercício
    python3 meu_pipeline.py           # o pipeline nos pedidos

Enquanto ajustar() e aplicar() não existirem, os testes falham. É o esperado.
"""
import sys
from pathlib import Path

import numpy as np  # noqa: F401  (você deve precisar)
import pandas as pd

BASE = Path("../dados/loja/pedidos_export_completo.csv")
FIM_TREINO = "2026-03-31"
FIM_VALIDACAO = "2026-05-31"
NUMERICAS = ["valor", "prazo_prometido_dias", "pedidos_anteriores", "cliente_novo"]
CATEGORIAS = ["categoria", "forma_pagamento", "canal"]
VEZES_MEDIANA = 10


def carregar():
    """Treino (janeiro a março) e validação (abril e maio). Junho, o teste, sai aqui."""
    if not BASE.exists():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 09-pipeline-para-dados-de-pessoas do kit.")
    e = pd.read_csv(BASE, parse_dates=["data_pedido"])
    e = e[e["data_pedido"] <= FIM_VALIDACAO]
    return e[e["data_pedido"] <= FIM_TREINO], e[e["data_pedido"] > FIM_TREINO]


def ajustar(treino):
    """Calcula com o treino todos os números do pipeline e retorna um dicionário com eles.

    O dicionário precisa ter as chaves "colunas" (a lista das colunas que aplicar() vai retornar,
    na ordem), "media" e "desvio" (um número por coluna de NUMERICAS). Recuse (ValueError)
    qualquer pedido de depois de FIM_TREINO.
    """
    raise NotImplementedError("escreva o ajustar")


def aplicar(params, pedidos):
    """A tabela que o modelo recebe, com as colunas de params["colunas"], mais "liberado" e "aviso".

    Use só os números de params. Uma linha por pedido, com o id_pedido no índice.
    """
    raise NotImplementedError("escreva o aplicar")


def main():
    treino, validacao = carregar()
    params = ajustar(treino)
    print(f"treino: {len(treino)} pedidos; validação: {len(validacao)}; junho fora")
    for c in NUMERICAS:
        print(f"  {c}: tira {params['media'][c]:.2f} e divide por {params['desvio'][c]:.2f}")
    print(f"  {len(params['colunas'])} colunas: {', '.join(params['colunas'])}")
    s = aplicar(params, validacao)
    print(f"validação: {len(s)} pedidos, {int(s['liberado'].sum())} liberados, "
          f"{int((s['aviso'] != '').sum())} com aviso")
    julho = pd.DataFrame([{"id_pedido": 9001, "data_pedido": pd.Timestamp("2026-07-02"), "categoria": "Casa",
                           "forma_pagamento": "pix", "valor": 180.0, "prazo_prometido_dias": 7, "cliente_novo": 1,
                           "pedidos_anteriores": 0, "canal": "marketplace"}])
    print(aplicar(params, julho).T.to_string())


if __name__ == "__main__":
    main()
