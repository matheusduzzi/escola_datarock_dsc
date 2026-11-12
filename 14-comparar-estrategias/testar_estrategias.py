"""Testes do estrategias.py, a peça que o experimento da aula usa. Rode de dentro da pasta da aula:

    python3 testar_estrategias.py

Casos pequenos montados aqui. Termina com código 0 quando tudo passa e 1 quando algum teste falha.
"""
import unittest

import numpy as np
import pandas as pd

import classificador
import estrategias as e


def caso(n=40, raros=8):
    g = np.random.Generator(np.random.PCG64(7))
    y = pd.Series(np.r_[np.ones(raros, dtype=int), np.zeros(n - raros, dtype=int)], index=range(100, 100 + n))
    x = pd.DataFrame({"a": g.normal(0, 1, n) + y.to_numpy(), "b_sim": (g.random(n) < 0.5).astype(float)},
                     index=y.index)
    return x, y


class Estrategias(unittest.TestCase):
    def test_proporcoes(self):
        x, y = caso()
        esperado = {"nenhuma": (40, 0.2), "peso de classe": (40, 0.5), "subamostragem": (16, 0.5),
                    "sobreamostragem": (64, 0.5), "SMOTE": (64, 0.5)}
        for nome, (linhas, prop) in esperado.items():
            xx, yy, pesos = e.ESTRATEGIAS[nome](x, y, 3)
            self.assertEqual((len(xx), len(yy)), (linhas, linhas), nome)
            self.assertAlmostEqual(e.proporcao(yy, pesos), prop, msg=nome)

    def test_entrada_intocada(self):
        x, y = caso()
        x0, y0 = x.copy(), y.copy()
        for nome, f in e.ESTRATEGIAS.items():
            f(x, y, 3)
            pd.testing.assert_frame_equal(x, x0, obj=f"{nome} mexeu no x que recebeu")
            pd.testing.assert_series_equal(y, y0, obj=f"{nome} mexeu no y que recebeu")

    def test_mesmo_sorteio(self):
        x, y = caso()
        for nome in e.SORTEIAM:
            a, b, c = e.ESTRATEGIAS[nome](x, y, 3), e.ESTRATEGIAS[nome](x, y, 3), e.ESTRATEGIAS[nome](x, y, 4)
            np.testing.assert_array_equal(a[0].to_numpy(), b[0].to_numpy(), err_msg=f"{nome}: mesmo sorteio")
            self.assertFalse(np.array_equal(a[0].to_numpy(), c[0].to_numpy()), f"{nome}: outro sorteio, outras linhas")

    def test_smote_fica_entre_raros(self):
        x, y = caso()
        xx, yy, _ = e.smote(x, y, 3)
        novos = xx.iloc[40:]
        raros = x[y == 1]
        self.assertTrue((yy.iloc[40:] == 1).all())
        self.assertTrue(((novos["a"] >= raros["a"].min()) & (novos["a"] <= raros["a"].max())).all(),
                        "cada linha nova fica entre dois cancelados de verdade")
        self.assertTrue(((novos["b_sim"] > 0) & (novos["b_sim"] < 1)).any(),
                        "numa coluna de 0 e 1, o SMOTE inventa valores no meio")

    def test_peso_um_e_o_classificador(self):
        x, y = caso()
        a = classificador.treinar(x, y)["pesos"]
        b = e.treinar(x, y, np.ones(len(y)))["pesos"]
        np.testing.assert_allclose(a, b, rtol=1e-10, atol=1e-12)

    def test_corrigir_nota(self):
        self.assertAlmostEqual(float(e.corrigir_nota([0.5], 0.5, 0.2)[0]), 0.2)
        self.assertAlmostEqual(float(e.corrigir_nota([0.3], 0.2, 0.2)[0]), 0.3, msg="mesma proporção, mesma nota")
        notas = np.array([0.1, 0.4, 0.7, 0.9])
        self.assertTrue((np.diff(e.corrigir_nota(notas, 0.5, 0.2)) > 0).all(), "a correção não muda a ordem")
        with self.assertRaises(ValueError):
            e.corrigir_nota([0.5], 0.0, 0.2)

    def test_y_invalido(self):
        x, y = caso()
        with self.assertRaises(ValueError):
            e.subamostragem(x, y.iloc[:30], 3)
        with self.assertRaises(ValueError):
            e.peso_de_classe(x, y.replace(1, 2), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
