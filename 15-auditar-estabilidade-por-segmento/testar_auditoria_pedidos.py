"""Testes das três funções do exercício, com pedidos montados aqui mesmo.

    python3 testar_auditoria_pedidos.py

Antes de você escrever as funções, os testes terminam com erro: é o ponto de partida.
"""
import unittest

import numpy as np
import pandas as pd

import auditoria_pedidos as a
import segmentos


def economia_do_enunciado(y, nota):
    """A conta do enunciado, escrita de novo aqui: R$ 15 por cancelado contra a lista."""
    y = np.asarray(y).astype(int)
    ligar = np.asarray(nota, dtype=float) > 5 / 15
    return 15 * y.sum() - (5 * ligar.sum() + 15 * (~ligar & (y == 1)).sum())


def tabela(linhas):
    return pd.DataFrame(linhas, columns=["categoria", "forma_pagamento", "cancelado", "nota"])


class Economia(unittest.TestCase):
    def test_economia_conta(self):
        # liga em 0,9, 0,5 e 0,4: R$ 15; o cancelado de nota 0,2 passa: R$ 15; nunca ligar: R$ 45
        self.assertEqual(a.economia([1, 1, 0, 0, 1], [0.9, 0.2, 0.5, 0.1, 0.4]), 15)

    def test_sem_ligacao_e_zero(self):
        self.assertEqual(a.economia([1, 0, 1], [0.1, 0.2, 0.3]), 0)

    def test_nota_no_empate_nao_liga(self):
        self.assertEqual(a.economia([0, 0], [1 / 3, 1 / 3]), 0)


class PorRecorte(unittest.TestCase):
    def setUp(self):
        linhas = ([("A", "pix", 1, 0.9)] * 30          # 30 cancelados, todos com ligação: R$ 10 cada
                  + [("B", "pix", 0, 0.9)] * 30        # 30 entregues, todos com ligação: -R$ 5 cada
                  + [("C", "boleto", 1, 0.9)] * 2 + [("C", "boleto", 0, 0.9)] * 8)
        self.v = tabela(linhas)

    def test_todos_os_valores_na_ordem(self):
        r = a.por_recorte(self.v, "categoria", ["C", "A", "Z", "B"])
        self.assertEqual([x["valor"] for x in r], ["C", "A", "Z", "B"])
        z = r[2]
        self.assertEqual((z["pedidos"], z["cancelados"], z["ligacoes"]), (0, 0, 0))
        self.assertIsNone(z["economia"])
        self.assertEqual(z["leitura"], "sem medida")

    def test_faixa_so_do_recorte(self):
        r = {x["valor"]: x for x in a.por_recorte(self.v, "categoria", ["A", "B"])}
        self.assertEqual(r["A"]["economia"], 300)
        self.assertEqual(tuple(r["A"]["faixa"]), (300, 300))
        self.assertEqual(r["A"]["leitura"], "ganha")
        self.assertEqual(r["B"]["economia"], -150)
        self.assertEqual(tuple(r["B"]["faixa"]), (-150, -150))
        self.assertEqual(r["B"]["leitura"], "perde")

    def test_faixa_que_cruza_o_zero(self):
        r = a.por_recorte(self.v, "categoria", ["C"])[0]
        c = self.v[self.v["categoria"] == "C"]
        esperado = segmentos.faixa(economia_do_enunciado, [c["cancelado"].to_numpy(), c["nota"].to_numpy()])
        self.assertEqual((r["pedidos"], r["cancelados"], r["ligacoes"], r["economia"]), (10, 2, 10, -20))
        self.assertEqual(tuple(r["faixa"]), esperado[:2])
        self.assertLess(r["faixa"][0], 0)
        self.assertGreater(r["faixa"][1], 0)
        self.assertEqual(r["leitura"], "não dá para dizer")


class Embaralhar(unittest.TestCase):
    def test_notas_iguais_nao_mudam_nada(self):
        # com todas as notas iguais, embaralhar não muda nada: o melhor e o pior são os de verdade,
        # e o melhor está na segunda coluna
        linhas = ([("A", "pix", 1, 0.9)] * 3 + [("A", "pix", 0, 0.9)] * 3
                  + [("B", "boleto", 1, 0.9)] * 2 + [("B", "boleto", 0, 0.9)] * 6
                  + [("B", "pix", 1, 0.9)] * 4 + [("A", "boleto", 1, 0.9)] * 1)
        v = tabela(linhas)
        reais = [economia_do_enunciado(v.loc[v[c] == x, "cancelado"], v.loc[v[c] == x, "nota"])
                 for c in ["categoria", "forma_pagamento"] for x in sorted(v[c].unique())]
        melhores, piores = a.embaralhar_recortes(v, ["categoria", "forma_pagamento"], vezes=30, sorteio=3)
        self.assertEqual(len(melhores), 30)
        self.assertEqual(len(piores), 30)
        self.assertEqual(set(melhores), {max(reais)})
        self.assertEqual(set(piores), {min(reais)})

    def test_mesmo_sorteio_mesmo_resultado(self):
        g = np.random.Generator(np.random.PCG64(0))
        v = tabela([(str(c), p, int(y), float(n)) for c, p, y, n in zip(
            g.choice(list("ABC"), 90), g.choice(["pix", "boleto"], 90), g.integers(0, 2, 90), g.random(90))])
        um = a.embaralhar_recortes(v, ["categoria"], vezes=40, sorteio=7)
        dois = a.embaralhar_recortes(v, ["categoria"], vezes=40, sorteio=7)
        outro = a.embaralhar_recortes(v, ["categoria"], vezes=40, sorteio=8)
        self.assertEqual(list(um[0]), list(dois[0]))
        self.assertEqual(list(um[1]), list(dois[1]))
        self.assertNotEqual(list(um[0]), list(outro[0]))


if __name__ == "__main__":
    unittest.main()
