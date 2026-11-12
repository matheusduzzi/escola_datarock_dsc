"""Testes do exercício: o pipeline do cancelamento. Rode de dentro da pasta da aula:

    python3 testar_meu_pipeline.py

Os testes importam o seu meu_pipeline.py. Eles não dizem como escrever o código; dizem o que o
pipeline precisa fazer. Os números esperados são calculados aqui, direto do CSV.
"""
import copy
import sys
import unittest

import numpy as np
import pandas as pd

import meu_pipeline as mp

if not mp.BASE.exists():
    sys.exit(f"não achei {mp.BASE}. Rode de dentro da pasta 09-pipeline-para-dados-de-pessoas do kit.")
E = pd.read_csv(mp.BASE, parse_dates=["data_pedido"])
TREINO = E[E["data_pedido"] <= "2026-03-31"]
VALIDACAO = E[(E["data_pedido"] > "2026-03-31") & (E["data_pedido"] <= "2026-05-31")]
DEPOIS = ["dias_ate_entrega", "contatos_sac", "cancelado"]


def um_pedido(**campos):
    p = {"id_pedido": 9001, "data_pedido": pd.Timestamp("2026-07-02"), "categoria": "Casa",
         "forma_pagamento": "pix", "valor": 180.0, "prazo_prometido_dias": 7, "cliente_novo": 1,
         "pedidos_anteriores": 0, "canal": "app"}
    p.update(campos)
    return pd.DataFrame([p])


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = mp.ajustar(TREINO)
        cls.colunas = cls.params["colunas"]

    def test_1_ajustar_recusa_pedido_depois_do_treino(self):
        with self.assertRaises(ValueError):
            mp.ajustar(pd.concat([TREINO, VALIDACAO]))
        with self.assertRaises(ValueError):
            mp.ajustar(pd.concat([TREINO, um_pedido()]))

    def test_2_colunas_do_treino(self):
        self.assertEqual(len(self.colunas), 14)
        self.assertIn("canal_app", self.colunas)
        self.assertIn("canal_site", self.colunas)
        for c in DEPOIS:
            self.assertFalse(any(c in col for col in self.colunas), c)

    def test_3_escala_do_treino(self):
        s = mp.aplicar(self.params, VALIDACAO)
        for c in ["valor", "prazo_prometido_dias"]:
            esperado = (VALIDACAO[c] - TREINO[c].mean()) / TREINO[c].std(ddof=0)
            self.assertTrue(np.allclose(s[c].to_numpy(), esperado.to_numpy()), c)

    def test_4_aplicar_nao_muda_o_ajuste(self):
        antes = copy.deepcopy(self.params)
        mp.aplicar(self.params, VALIDACAO)
        self.assertEqual(self.params, antes)

    def test_5_um_pedido_igual_ao_lote(self):
        lote = mp.aplicar(self.params, VALIDACAO.head(60))
        um_a_um = pd.concat([mp.aplicar(self.params, VALIDACAO.iloc[[i]]) for i in range(60)])
        self.assertEqual(list(lote.columns), self.colunas + ["liberado", "aviso"])
        pd.testing.assert_frame_equal(lote, um_a_um, check_dtype=False)

    def test_6_canal_novo_zerado_e_avisado(self):
        s = mp.aplicar(self.params, um_pedido(canal="marketplace"))
        self.assertEqual(list(s.columns), self.colunas + ["liberado", "aviso"])
        s = s.iloc[0]
        self.assertTrue(bool(s["liberado"]))
        self.assertEqual(float(s["canal_app"]) + float(s["canal_site"]), 0)
        self.assertIn("canal", s["aviso"])

    def test_7_vazio_sem_nota(self):
        for campo in ["prazo_prometido_dias", "categoria", "valor"]:
            s = mp.aplicar(self.params, um_pedido(**{campo: None})).iloc[0]
            self.assertFalse(bool(s["liberado"]), campo)
            self.assertNotEqual(s["aviso"], "", campo)

    def test_8_valor_alto_avisa_sem_mudar(self):
        alto = 11 * TREINO.loc[TREINO["categoria"] == "Casa", "valor"].median()
        s = mp.aplicar(self.params, um_pedido(valor=alto)).iloc[0]
        self.assertTrue(bool(s["liberado"]))
        self.assertNotEqual(s["aviso"], "")
        esperado = (alto - TREINO["valor"].mean()) / TREINO["valor"].std(ddof=0)
        self.assertAlmostEqual(float(s["valor"]), esperado)
        self.assertEqual(mp.aplicar(self.params, um_pedido()).iloc[0]["aviso"], "")

    def test_9_colunas_de_depois_nao_mudam_nada(self):
        mexido = VALIDACAO.assign(dias_ate_entrega=0, contatos_sac=9, cancelado=1)
        pd.testing.assert_frame_equal(mp.aplicar(self.params, mexido), mp.aplicar(self.params, VALIDACAO),
                                      check_dtype=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
