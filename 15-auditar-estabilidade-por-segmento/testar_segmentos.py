"""Testes do segmentos.py.

    python3 testar_segmentos.py
"""
import unittest

import numpy as np

import segmentos as s


def media(x):
    return float(np.mean(x))


class Faixa(unittest.TestCase):
    def test_recorte_igual_tem_faixa_de_um_ponto(self):
        self.assertEqual(s.faixa(media, [[7] * 20]), (7.0, 7.0, 1000))

    def test_faixa_contem_o_valor_e_tira_25_de_cada_lado(self):
        x = np.r_[np.ones(10), np.zeros(30)]
        baixo, alto, validos = s.faixa(media, [x], sorteios=1000, sorteio=1)
        self.assertEqual(validos, 1000)
        self.assertLess(baixo, 0.25)
        self.assertGreater(alto, 0.25)
        g = s.gerador(1)
        valores = sorted(float(x[g.integers(0, 40, 40)].mean()) for _ in range(1000))
        self.assertEqual((baixo, alto), (valores[25], valores[974]))

    def test_sorteio_sem_medida_fica_fora(self):
        x = np.r_[1, np.zeros(19)]
        baixo, alto, validos = s.faixa(lambda v: None if v.sum() == 0 else 1.0, [x], sorteios=200)
        self.assertLess(validos, 200)
        self.assertEqual((baixo, alto), (1.0, 1.0))

    def test_poucos_sorteios_validos_ou_recorte_vazio(self):
        self.assertEqual(s.faixa(lambda v: None, [[1, 2, 3]], sorteios=100)[:2], (None, None))
        self.assertEqual(s.faixa(media, [[]]), (None, None, 0))

    def test_colunas_de_tamanhos_diferentes(self):
        with self.assertRaises(ValueError):
            s.faixa(lambda a, b: 0, [[1, 2], [1]])


class Leitura(unittest.TestCase):
    def test_as_quatro_leituras(self):
        self.assertEqual(s.leitura(10, 50), "ganha")
        self.assertEqual(s.leitura(-50, -10), "perde")
        self.assertEqual(s.leitura(-10, 50), "não dá para dizer")
        self.assertEqual(s.leitura(0, 50), "não dá para dizer")
        self.assertEqual(s.leitura(None, None), "sem medida")


class Embaralhar(unittest.TestCase):
    def test_embaralha_as_notas_e_repete_com_o_mesmo_sorteio(self):
        notas = np.arange(10, dtype=float)
        recortes = [np.arange(10) < 5, np.arange(10) >= 5]
        um = s.embaralhar(notas, recortes, lambda n, m: n.sum(), vezes=50, sorteio=2)
        dois = s.embaralhar(notas, recortes, lambda n, m: n.sum(), vezes=50, sorteio=2)
        self.assertEqual(um, dois)
        self.assertTrue(all(b + p == 45 for b, p in zip(*um)))   # as notas só trocam de lugar
        self.assertTrue(all(b >= p for b, p in zip(*um)))
        self.assertGreater(len(set(um[0])), 1)


if __name__ == "__main__":
    unittest.main()
