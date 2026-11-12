"""Testes da aplicar_regua() do exercício da aula «Decidir pelo critério».

    python3 testar_decidir_rh.py

Os casos são pequenos e feitos à mão. Nenhum deles abre o teste das admissões.
"""
import json
import unittest
from pathlib import Path

from decidir import diferencas
from decidir_rh import aplicar_regua

REGUA = {"precisao_minima": 0.40, "revocacao_minima": 0.25, "saldo_maior_que": 0, "vagas_mes": 12}


def medida(precisao=0.5, revocacao=0.3, saldo=750, maior_mes=10):
    return {"precisao": precisao, "revocacao": revocacao, "saldo": saldo, "maior_mes": maior_mes}


def passam(condicoes):
    return [passa for _, passa in condicoes]


class TestAplicarRegua(unittest.TestCase):
    def test_tudo_passa(self):
        condicoes, decisao = aplicar_regua(medida(), REGUA)
        self.assertEqual(len(condicoes), 4)
        self.assertEqual(passam(condicoes), [True, True, True, True])
        self.assertEqual(decisao, "uso")

    def test_uma_falha_basta(self):
        casos = [(medida(precisao=0.36), 0), (medida(revocacao=0.20), 1),
                 (medida(saldo=-240), 2), (medida(maior_mes=13), 3)]
        for m, qual in casos:
            with self.subTest(falha=qual):
                condicoes, decisao = aplicar_regua(m, REGUA)
                esperado = [True] * 4
                esperado[qual] = False
                self.assertEqual(passam(condicoes), esperado)
                self.assertEqual(decisao, "não uso")

    def test_no_limite(self):
        # "pelo menos" e "no máximo" incluem o limite; "saldo maior que zero" não inclui o zero
        condicoes, decisao = aplicar_regua(medida(precisao=0.40, revocacao=0.25, maior_mes=12), REGUA)
        self.assertEqual(passam(condicoes), [True, True, True, True])
        self.assertEqual(decisao, "uso")
        condicoes, decisao = aplicar_regua(medida(saldo=0), REGUA)
        self.assertEqual(passam(condicoes), [True, True, False, True])
        self.assertEqual(decisao, "não uso")

    def test_ninguem_marcado(self):
        # uma regra que não marca ninguém não tem precisão: zero dividido por zero não passa
        condicoes, decisao = aplicar_regua(medida(precisao=None, revocacao=0.0, saldo=0, maior_mes=0), REGUA)
        self.assertEqual(passam(condicoes), [False, False, False, True])
        self.assertEqual(decisao, "não uso")

    def test_a_regua_vem_do_plano(self):
        # os limites saem do plano, não do código
        outra = dict(REGUA, precisao_minima=0.60, vagas_mes=5)
        condicoes, decisao = aplicar_regua(medida(), outra)
        self.assertEqual(passam(condicoes), [False, True, True, False])
        self.assertEqual(decisao, "não uso")

    def test_tres_de_quatro_nao_basta(self):
        condicoes, decisao = aplicar_regua(medida(precisao=0.30), REGUA)
        self.assertEqual(sum(passam(condicoes)), 3)
        self.assertEqual(decisao, "não uso")


class TestPlanoDoRafael(unittest.TestCase):
    def test_o_plano_do_rafael_muda_corte_e_regua(self):
        marta = json.loads(Path("regua_rh.json").read_text(encoding="utf-8"))
        rafael = json.loads(Path("regua-rh-do-rafael.json").read_text(encoding="utf-8"))
        campos = [linha.split(":")[0] for linha in diferencas(marta, rafael)]
        self.assertEqual(campos, ["corte", "escrito_em", "regua.precisao_minima"])
        self.assertEqual(diferencas(marta, marta), [])


if __name__ == "__main__":
    unittest.main()
