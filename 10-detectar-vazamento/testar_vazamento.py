"""Os testes de vazamento da preparação do cancelamento. Rode de dentro da pasta da aula:

    python3 testar_vazamento.py pipeline_rafael       # a preparação do Rafael: falha
    python3 testar_vazamento.py pipeline_corrigido    # a preparação corrigida: passa

O nome depois do comando é o arquivo da preparação, sem o .py. Ele precisa ter preparar(base),
que retorna x_treino, y_treino, x_validacao, y_validacao.

A ideia dos testes: mudar o que a preparação não pode saber e ver se o resultado muda.
Se a tabela do treino muda quando eu mexo em junho, junho entrou na conta.
"""
import importlib
import sys
import unittest
from pathlib import Path

import pandas as pd

from classificador import pct, varrer
from ferramentas_teste import iguais, rodar

BASE = Path("../dados/loja/pedidos_export_completo.csv")
FIM_TREINO = pd.Timestamp("2026-03-31")
FIM_VALIDACAO = pd.Timestamp("2026-05-31")
NASCEM_DEPOIS = ["dias_ate_entrega", "contatos_sac"]
LIMITE = 0.95

if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
    sys.exit("diga qual preparação testar, por exemplo: python3 testar_vazamento.py pipeline_corrigido")
NOME = sys.argv[1].removesuffix(".py")
if not BASE.exists():
    sys.exit(f"não achei {BASE}. Rode de dentro da pasta 10-detectar-vazamento do kit.")
PREP = importlib.import_module(NOME)
E = pd.read_csv(BASE, parse_dates=["data_pedido"])


class Vazamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x_tr, cls.y_tr, cls.x_va, cls.y_va = PREP.preparar(E.copy())

    def test_1_colunas_que_nascem_depois_nao_mudam_nada(self):
        mexido = E.assign(dias_ate_entrega=0, contatos_sac=0)
        x_tr, _, x_va, _ = PREP.preparar(mexido)
        self.assertTrue(iguais(x_tr, self.x_tr) and iguais(x_va, self.x_va),
                        "zerar dias_ate_entrega e contatos_sac mudou a tabela: uma coluna de depois do pedido entrou")

    def test_2_nenhuma_coluna_sozinha_le_a_resposta(self):
        base = self.x_tr.assign(alvo=self.y_tr.to_numpy())
        aucs = varrer(base, "alvo")
        self.assertLess(aucs.iloc[0], LIMITE,
                        f"a coluna {aucs.index[0]} sozinha acerta {pct(aucs.iloc[0])} dos pares no treino")

    def test_3_resposta_de_depois_do_treino_nao_entra(self):
        depois = E["data_pedido"] > FIM_TREINO
        mexido = E.copy()
        mexido.loc[depois, "cancelado"] = 1 - mexido.loc[depois, "cancelado"]
        x_tr, _, x_va, _ = PREP.preparar(mexido)
        self.assertTrue(iguais(x_tr, self.x_tr) and iguais(x_va, self.x_va),
                        "inverter o cancelado de abril a junho mudou a tabela: a resposta da validação ou do teste entrou")

    def test_4_teste_fechado(self):
        junho = E["data_pedido"] > FIM_VALIDACAO
        mexido = E.copy()
        mexido.loc[junho, "valor"] = mexido.loc[junho, "valor"] * 10
        mexido.loc[junho, "prazo_prometido_dias"] = mexido.loc[junho, "prazo_prometido_dias"] + 10
        mexido.loc[junho, "pedidos_anteriores"] = mexido.loc[junho, "pedidos_anteriores"] + 5
        mexido.loc[junho, "categoria"] = "Casa"
        x_tr, _, x_va, _ = PREP.preparar(mexido)
        self.assertTrue(iguais(x_tr, self.x_tr) and iguais(x_va, self.x_va),
                        "mexer nos pedidos de junho mudou o treino ou a validação: o teste entrou na preparação")

    def test_5_validacao_so_mede(self):
        va = (E["data_pedido"] > FIM_TREINO) & (E["data_pedido"] <= FIM_VALIDACAO)
        mexido = E.copy()
        mexido.loc[va, "valor"] = mexido.loc[va, "valor"] * 10
        x_tr, _, _, _ = PREP.preparar(mexido)
        self.assertTrue(iguais(x_tr, self.x_tr),
                        "mexer no valor de abril e maio mudou a tabela do treino: a validação ajudou a ajustar")


if __name__ == "__main__":
    print(f"preparação testada: {NOME}.py")
    sys.exit(rodar(Vazamento))
