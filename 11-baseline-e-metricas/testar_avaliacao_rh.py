"""Testes da linha() e das regras() do exercício. Rode de dentro da pasta da aula:

    python3 testar_avaliacao_rh.py

Os casos são pequenos e feitos à mão: eles não usam as admissões nem mostram a tabela da
validação. Termina com código 0 quando tudo passa e 1 quando algum teste falha.
"""
import unittest

import numpy as np
import pandas as pd

import avaliacao_rh as rh


class Linha(unittest.TestCase):
    def setUp(self):
        # 6 pessoas: saíram a 1ª, a 2ª e a 5ª; a regra acompanha a 1ª, a 3ª e a 5ª
        self.y = np.array([1, 1, 0, 0, 1, 0])
        self.marcar = np.array([True, False, True, False, True, False])
        self.mes = np.array(["2025-07", "2025-07", "2025-07", "2025-08", "2025-08", "2025-08"])

    def test_matriz_e_metricas(self):
        r = rh.linha(self.y, self.marcar, self.mes)
        self.assertEqual((r["vp"], r["fp"], r["fn"]), (2, 1, 1), "VP, FP e FN do caso de 6 pessoas")
        self.assertEqual(r["marcadas"], 3)
        self.assertAlmostEqual(r["precisao"], 2 / 3, msg="precisão: VP sobre as marcadas")
        self.assertAlmostEqual(r["revocacao"], 2 / 3, msg="revocação: VP sobre quem saiu")

    def test_maior_mes(self):
        r = rh.linha(self.y, self.marcar, self.mes)
        self.assertEqual(r["maior_mes"], 2, "julho tem 2 acompanhadas e agosto tem 1")

    def test_saldo_com_o_efeito(self):
        r = rh.linha(self.y, self.marcar, self.mes)
        # 2 acertos evitam, em média, 2 × 3000 × 1/4; os 3 acompanhamentos custam 3 × 240
        self.assertAlmostEqual(r["saldo"], 2 * 750 - 3 * 240,
                               msg="o acompanhamento evita só 1 de cada 4 saídas: o acerto vale R$ 750")

    def test_ninguem_marcado(self):
        r = rh.linha(self.y, np.zeros(6, dtype=bool), self.mes)
        self.assertIsNone(r["precisao"], "sem ninguém marcado, a precisão não existe: None, não 0")
        self.assertEqual((r["marcadas"], r["maior_mes"], r["vp"], r["fn"]), (0, 0, 0, 3))
        self.assertAlmostEqual(r["saldo"], 0, msg="não acompanhar ninguém é a régua do saldo: 0")
        self.assertAlmostEqual(r["revocacao"], 0)

    def test_tamanhos_diferentes(self):
        with self.assertRaises(ValueError, msg="y e marcar com tamanhos diferentes têm que dar erro"):
            rh.linha(self.y, self.marcar[:5], self.mes)


class Regras(unittest.TestCase):
    def test_quatro_regras(self):
        v = pd.DataFrame({"mes": ["2025-07"] * 4, "turno": ["noite", "manha", "noite", "tarde"],
                          "saiu_180d": [1, 0, 0, 1], "nota": [0.10, 0.33, 0.31, 0.90]},
                         index=[11, 12, 13, 14])
        r = rh.regras(v)
        self.assertEqual(list(r), ["ninguém", "todos", "turno da noite", "classificador, nota acima do empate"])
        lista = {k: list(pd.Series(m, index=v.index).astype(bool)) for k, m in r.items()}
        self.assertEqual(lista["ninguém"], [False] * 4)
        self.assertEqual(lista["todos"], [True] * 4)
        self.assertEqual(lista["turno da noite"], [True, False, True, False])
        self.assertEqual(lista["classificador, nota acima do empate"], [False, True, False, True],
                         "o corte é o empate de 0,32: 0,33 entra, 0,31 fica fora")


if __name__ == "__main__":
    unittest.main(verbosity=2)
