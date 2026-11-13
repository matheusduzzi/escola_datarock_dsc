"""Os seus testes de vazamento da lista do dia 7. Exercício da aula «Detectar vazamento».

Rode de dentro da pasta da aula, com o nome da preparação depois do comando:

    python3 meus_testes.py acompanhamento_rafael    # tem que falhar
    python3 meus_testes.py meu_acompanhamento       # a sua correção: tem que passar

A preparação testada precisa ter preparar(base), que recebe as 1500 admissões e retorna
x_treino, y_treino, x_validacao, y_validacao. O começo já está pronto: a base lida, as datas e
a tabela de referência em setUpClass. Escreva os testes dentro da classe, um método test_ por
coisa que a preparação não pode saber. Use os testes da demonstração (testar_vazamento.py) como
ponto de partida.
"""
import importlib
import sys
import unittest
from pathlib import Path

import pandas as pd

from classificador import pct, varrer  # noqa: F401  (você pode precisar)
from ferramentas_teste import iguais, rodar  # noqa: F401

BASE = Path("../dados/pessoas/admissoes.csv")
FIM_TREINO = pd.Timestamp("2025-06-30")
FIM_VALIDACAO = pd.Timestamp("2025-09-30")

if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
    sys.exit("diga qual preparação testar, por exemplo: python3 meus_testes.py acompanhamento_rafael")
NOME = sys.argv[1].removesuffix(".py")
if not BASE.exists():
    sys.exit(f"não achei {BASE}. Rode de dentro da pasta 10-detectar-vazamento do kit.")
PREP = importlib.import_module(NOME)
A = pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])


class Vazamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x_tr, cls.y_tr, cls.x_va, cls.y_va = PREP.preparar(A.copy())

    def test_escreva_os_seus_testes(self):
        self.fail("apague esse teste e escreva os seus")


if __name__ == "__main__":
    print(f"preparação testada: {NOME}.py")
    sys.exit(rodar(Vazamento))
