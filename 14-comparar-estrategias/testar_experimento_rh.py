"""Testes da avaliar() e da conferir() do exercício. Rode de dentro da pasta da aula:

    python3 testar_experimento_rh.py

Os casos são pequenos: 60 pessoas de treino e 20 de validação, montadas aqui mesmo, com duas
colunas. Eles não usam as admissões nem mostram a tabela do exercício. Termina com código 0
quando tudo passa e 1 quando algum teste falha.
"""
import copy
import unittest

import numpy as np
import pandas as pd

import classificador
import estrategias as e
import experimento_rh as rh


def caso():
    """60 pessoas de treino (15 saíram) e 20 de validação (5 saíram), em julho e agosto."""
    gerador = np.random.Generator(np.random.PCG64(2025))
    def parte(n, saidas, inicio):
        y = np.r_[np.ones(saidas, dtype=int), np.zeros(n - saidas, dtype=int)]
        x = pd.DataFrame({"a": gerador.normal(0, 1, n) + 1.2 * y, "b": gerador.normal(0, 1, n) - 0.6 * y},
                         index=range(inicio, inicio + n))
        return x, pd.Series(y, index=x.index)
    x_tr, y_tr = parte(60, 15, 1)
    x_va, y_va = parte(20, 5, 101)
    mes = pd.Series(["2025-07"] * 12 + ["2025-08"] * 8, index=x_va.index)
    return {"x_tr": x_tr, "y_tr": y_tr, "x_va": x_va, "y_va": y_va, "mes": mes, "sha256": "abc"}


class Avaliar(unittest.TestCase):
    def setUp(self):
        self.d = caso()

    def test_validacao_intacta(self):
        for nome in e.ESTRATEGIAS:
            r = rh.avaliar(self.d, nome, 3)
            self.assertEqual((r["n"], r["saidas"]), (20, 5),
                             f"{nome}: a estratégia mexe só no treino; a validação tem 20 pessoas e 5 saídas")

    def test_mesmo_sorteio_mesmo_resultado(self):
        for nome in e.ESTRATEGIAS:
            self.assertEqual(rh.avaliar(self.d, nome, 3), rh.avaliar(self.d, nome, 3),
                             f"{nome}: o mesmo sorteio tem que dar o mesmo resultado")
        self.assertEqual(rh.avaliar(self.d, "nenhuma", 1), rh.avaliar(self.d, "nenhuma", 2),
                         "nenhuma não sorteia nada: o sorteio não muda o resultado")

    def test_nota_corrigida(self):
        # a subamostragem com o sorteio 0: o modelo viu 50% de saídas, e o treino tem 25%
        x, y, pesos = e.subamostragem(self.d["x_tr"], self.d["y_tr"], 0)
        nota = classificador.nota(e.treinar(x, y, pesos), self.d["x_va"])
        corrigida = e.corrigir_nota(nota, 0.5, 0.25)
        sem, com = int((nota > rh.EMPATE).sum()), int((corrigida > rh.EMPATE).sum())
        self.assertNotEqual(sem, com, "o caso foi montado para a correção mudar a lista")
        self.assertEqual(rh.avaliar(self.d, "subamostragem", 0)["marcadas"], com,
                         "a nota é corrigida para a proporção do treino antes do corte de 0,32")

    def test_saldo_com_o_efeito(self):
        for nome in e.ESTRATEGIAS:
            r = rh.avaliar(self.d, nome, 3)
            self.assertAlmostEqual(r["saldo"], r["vp"] * 750 - r["marcadas"] * 240,
                                   msg=f"{nome}: cada acerto vale 1/4 de R$ 3.000; cada acompanhamento custa R$ 240")
            self.assertLessEqual(r["maior_mes"], r["marcadas"])
            if r["marcadas"]:
                self.assertAlmostEqual(r["precisao"], r["vp"] / r["marcadas"])

    def test_ninguem_marcado(self):
        d = caso()
        d["y_va"] = pd.Series(0, index=d["x_va"].index)
        d["x_va"] = d["x_va"].assign(a=-50.0, b=50.0)   # longe de quem sai: ninguém passa do corte
        r = rh.avaliar(d, "nenhuma", 0)
        self.assertEqual((r["marcadas"], r["maior_mes"], r["vp"]), (0, 0, 0))
        self.assertIsNone(r["precisao"], "sem ninguém marcado, a precisão não existe: None, não 0")


class Conferir(unittest.TestCase):
    def setUp(self):
        self.reg = {"dados": {"arquivo": "a.csv", "sha256": "abc"},
                    "parametros": {"sorteio": 14, "sorteios": [0, 1, 2]},
                    "versoes": {"python": "3.12.1", "numpy": "2.1.0"},
                    "resultados": {"um_sorteio": {"nenhuma": {"saldo": -1830.0, "marcadas": 67}},
                                   "vinte_sorteios": {"subamostragem": [-2790.0, -1470.0, -4890.0]}}}

    def test_iguais(self):
        self.assertEqual(rh.conferir(self.reg, copy.deepcopy(self.reg)), ([], []))

    def test_dados_mudados(self):
        novo = copy.deepcopy(self.reg)
        novo["dados"]["sha256"] = "def"
        erros, _ = rh.conferir(self.reg, novo)
        self.assertEqual(len(erros), 1, "outro arquivo de dados é uma diferença")
        self.assertIn("sha256", erros[0])

    def test_resultado_mudado(self):
        novo = copy.deepcopy(self.reg)
        novo["resultados"]["vinte_sorteios"]["subamostragem"][1] = -1200.0
        novo["parametros"]["sorteio"] = 7
        erros, avisos = rh.conferir(self.reg, novo)
        self.assertEqual(len(erros), 2, "o sorteio e o saldo mudaram: duas diferenças")
        self.assertEqual(avisos, [])

    def test_versao_e_aviso(self):
        novo = copy.deepcopy(self.reg)
        novo["versoes"]["numpy"] = "2.3.0"
        erros, avisos = rh.conferir(self.reg, novo)
        self.assertEqual(erros, [], "versão diferente não é erro")
        self.assertEqual(len(avisos), 1, "mas aparece como aviso")
        self.assertIn("numpy", avisos[0])

    def test_chave_faltando(self):
        novo = copy.deepcopy(self.reg)
        del novo["resultados"]["um_sorteio"]["nenhuma"]["marcadas"]
        erros, _ = rh.conferir(self.reg, novo)
        self.assertEqual(len(erros), 1, "um número que sumiu do registro novo é uma diferença")
        self.assertIn("marcadas", erros[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
