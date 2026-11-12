"""Testes do pipeline do acompanhamento. Rode de dentro da pasta da aula:

    python3 testar_pipeline.py

Cada teste diz numa frase o que o pipeline promete. Os números esperados são calculados aqui,
direto do CSV, sem passar pelo pipeline.
"""
import copy
import unittest

import numpy as np
import pandas as pd

import pipeline as pl

A = pl.carregar()
TREINO, VALIDACAO, N_TESTE, NOVAS = pl.separar(A)


def uma_pessoa(**campos):
    """Uma pessoa contratada em julho de 2026, com os campos trocados pelo teste."""
    p = {"id_pessoa": 9001, "data_admissao": pd.Timestamp("2026-07-06"), "loja": "L03", "cargo": "caixa",
         "turno": "tarde", "salario_base": 2100, "distancia_km": 3.0, "indicacao": 0}
    p.update(campos)
    return pd.DataFrame([p])


class Ajustar(unittest.TestCase):
    def setUp(self):
        self.params = pl.ajustar(TREINO)

    def test_recusa_linha_de_depois_do_treino(self):
        with self.assertRaises(ValueError):
            pl.ajustar(pd.concat([TREINO, VALIDACAO]))
        with self.assertRaises(ValueError):
            pl.ajustar(pd.concat([TREINO, NOVAS.head(1)]))

    def test_numeros_sao_os_do_treino(self):
        t = A[(A["data_admissao"] < "2025-07-01")]
        dias = (t["data_desligamento"] - t["data_admissao"]).dt.days
        t = t[~(dias <= 7)]
        self.assertEqual(len(t), 787)
        self.assertAlmostEqual(self.params["mediana_distancia"], t["distancia_km"].median())
        med = t.groupby("cargo")["salario_base"].median()
        self.assertEqual(self.params["mediana_salario_cargo"], {k: float(v) for k, v in med.items()})
        s = t["salario_base"].copy()
        ref = t["cargo"].map(med)
        s[(s > 2 * ref) | (s < ref / 2)] = ref
        self.assertAlmostEqual(self.params["media"]["salario_base"], s.mean())
        self.assertAlmostEqual(self.params["desvio"]["salario_base"], float(np.std(s.to_numpy())))
        self.assertEqual(len(self.params["colunas"]), 17)

    def test_nao_usa_a_resposta(self):
        mexido = TREINO.assign(saiu_180d=1 - TREINO["saiu_180d"], data_desligamento=pd.NaT,
                               horas_treinamento=0)
        self.assertEqual(pl.ajustar(mexido), self.params)

    def test_teste_fechado(self):
        b = A.copy()
        dias = (b["data_desligamento"] - b["data_admissao"]).dt.days
        t = (b["data_admissao"] > pl.FIM_VALIDACAO) & (b["data_admissao"] <= pl.FIM_CONTRATO) & ~(dias <= 7)
        self.assertEqual(int(t.sum()), N_TESTE)
        b.loc[t, ["loja", "cargo", "turno"]] = ["L99", "gerente", "madrugada"]
        b.loc[t, ["salario_base", "distancia_km"]] = [99999, 999.0]
        tr, va, _, _ = pl.separar(b)
        self.assertEqual(pl.ajustar(tr), self.params)
        pd.testing.assert_frame_equal(pl.aplicar(pl.ajustar(tr), va), pl.aplicar(self.params, VALIDACAO))


class Aplicar(unittest.TestCase):
    def setUp(self):
        self.params = pl.ajustar(TREINO)

    def test_nao_muda_o_que_foi_ajustado(self):
        antes = copy.deepcopy(self.params)
        pl.aplicar(self.params, NOVAS)
        self.assertEqual(self.params, antes)

    def test_usa_a_escala_do_treino(self):
        s = pl.aplicar(self.params, VALIDACAO)
        esperado = (VALIDACAO["distancia_km"].fillna(self.params["mediana_distancia"])
                    - self.params["media"]["distancia_km"]) / self.params["desvio"]["distancia_km"]
        self.assertTrue(np.allclose(s["distancia_km"].to_numpy(), esperado.to_numpy()))
        self.assertGreater(abs(s["distancia_km"].mean()), 0.1)  # recalculada na validação, daria 0

    def test_uma_pessoa_igual_ao_lote(self):
        lote = pl.aplicar(self.params, NOVAS)
        um_a_um = pd.concat([pl.aplicar(self.params, NOVAS.iloc[[i]]) for i in range(len(NOVAS))])
        pd.testing.assert_frame_equal(lote, um_a_um)

    def test_colunas_fixas(self):
        for base in (NOVAS, NOVAS.head(1), VALIDACAO, uma_pessoa(loja="L08", cargo="atendimento digital")):
            s = pl.aplicar(self.params, base)
            self.assertEqual(list(s.columns), self.params["colunas"] + ["liberada", "aviso"])

    def test_colunas_que_ficam_fora(self):
        mexido = NOVAS.assign(saiu_180d=1, data_desligamento=pd.Timestamp("2026-06-01"), horas_treinamento=0)
        pd.testing.assert_frame_equal(pl.aplicar(self.params, mexido), pl.aplicar(self.params, NOVAS))
        s = pl.aplicar(self.params, NOVAS)
        for c in ["saiu_180d", "data_desligamento", "horas_treinamento", "data_admissao"]:
            self.assertNotIn(c, s.columns)

    def test_loja_e_cargo_novos_zerados_e_avisados(self):
        s = pl.aplicar(self.params, uma_pessoa(loja="L08", cargo="atendimento digital")).iloc[0]
        self.assertTrue(s["liberada"])
        self.assertEqual(s.filter(like="loja_").sum(), 0)
        self.assertEqual(s.filter(like="cargo_").sum(), 0)
        self.assertIn("loja que o treino não tem", s["aviso"])
        self.assertIn("cargo que o treino não tem", s["aviso"])
        s = pl.aplicar(self.params, uma_pessoa(turno="madrugada")).iloc[0]
        self.assertIn("turno que o treino não tem", s["aviso"])

    def test_categoria_vazia_sem_nota(self):
        for campo in ["loja", "cargo", "turno", "indicacao", "salario_base"]:
            s = pl.aplicar(self.params, uma_pessoa(**{campo: None})).iloc[0]
            self.assertFalse(s["liberada"], campo)
            self.assertTrue(s[self.params["colunas"]].isna().all(), campo)
            self.assertNotEqual(s["aviso"], "", campo)
        s = pl.aplicar(self.params, uma_pessoa(indicacao=2)).iloc[0]
        self.assertFalse(s["liberada"])

    def test_distancia_vazia_e_fora_da_faixa(self):
        vazia = pl.aplicar(self.params, uma_pessoa(distancia_km=None)).iloc[0]
        fora = pl.aplicar(self.params, uma_pessoa(distancia_km=-3.0)).iloc[0]
        longe = pl.aplicar(self.params, uma_pessoa(distancia_km=450.0)).iloc[0]
        mediana = (self.params["mediana_distancia"] - self.params["media"]["distancia_km"]) \
            / self.params["desvio"]["distancia_km"]
        for s in (vazia, fora, longe):
            self.assertTrue(s["liberada"])
            self.assertAlmostEqual(s["distancia_km"], mediana)
        self.assertEqual(vazia["aviso"], "")
        self.assertIn("distância fora da faixa", fora["aviso"])
        self.assertIn("distância fora da faixa", longe["aviso"])

    def test_salario_fora_da_faixa(self):
        s = pl.aplicar(self.params, uma_pessoa(salario_base=21100)).iloc[0]
        caixa = (2110 - self.params["media"]["salario_base"]) / self.params["desvio"]["salario_base"]
        self.assertAlmostEqual(s["salario_base"], caixa)
        self.assertIn("salário fora da faixa do cargo", s["aviso"])
        s = pl.aplicar(self.params, uma_pessoa(cargo="atendimento digital", salario_base=3000)).iloc[0]
        self.assertNotIn("salário", s["aviso"])  # 3000 cabe entre a metade e o dobro de 2210

    def test_recusa_quem_nao_foi_contratado(self):
        with self.assertRaises(ValueError):
            pl.aplicar(self.params, uma_pessoa(data_admissao=pd.NaT))
        with self.assertRaises(ValueError):
            pl.aplicar(self.params, uma_pessoa().drop(columns="data_admissao"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
