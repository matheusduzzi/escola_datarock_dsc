"""Os testes do exercício: as três checar_*() de achados_rh.py e o preparar() de consertar_rh.py.

    python3 testar_achados_rh.py

Os primeiros casos usam pessoas pequenas, feitas à mão, com o resultado que o contrato do alvo da
aula 03 pede. Os últimos rodam nas 1500 admissões: as perguntas têm que achar os defeitos do
projeto da consultoria e não achar nada no pipeline da aula 09 nem no seu conserto.
"""
import unittest

import pandas as pd

import achados_rh as ach


def pessoa(i, admissao, saida=None, loja="L01", salario=2000, distancia=5.0):
    adm = pd.Timestamp(admissao)
    des = pd.Timestamp(saida) if saida else pd.NaT
    dias = (des - adm).days if saida else None
    completou = adm + pd.Timedelta(days=180) <= pd.Timestamp("2026-06-30")
    rot = 1.0 if dias is not None and dias <= 180 else (0.0 if completou else float("nan"))
    return {"id_pessoa": i, "data_admissao": adm, "loja": loja, "cargo": "caixa", "turno": "manha",
            "salario_base": salario, "distancia_km": distancia, "indicacao": 0, "horas_treinamento": 20,
            "data_desligamento": des, "saiu_180d": rot}


def base(*linhas):
    return pd.DataFrame(list(linhas))


def rotulos(**por_id):
    return pd.Series({int(k[1:]): v for k, v in por_id.items()})


# --------------------------------------------------------------------------- alvo

class Alvo(unittest.TestCase):
    b = base(pessoa(1, "2025-01-10", "2025-03-01"),       # saiu no dia 50: 1
             pessoa(2, "2025-01-10"),                     # ficou: 0
             pessoa(3, "2024-12-26", "2025-06-24"),       # saiu no dia 180: ainda conta, 1
             pessoa(4, "2025-02-07", "2025-08-10"),       # saiu no dia 184: 0
             pessoa(5, "2025-03-03", "2025-03-10"),       # saiu no dia 7: fora
             pessoa(6, "2026-01-01"),                     # completou 180 dias na extração: 0
             pessoa(7, "2026-01-02"),                     # a turma ainda não tem resposta: fora
             pessoa(8, "2026-01-02", "2026-02-11"))       # saiu no dia 40, mas a turma não tem resposta: fora

    def test_rotulos_do_contrato_passam(self):
        r = ach.checar_alvo(self.b, rotulos(p1=1, p2=0, p3=1, p4=0, p6=0))
        self.assertEqual(r, {"saiu_ate_o_dia_7": 0, "depois_de_2026_01_01": 0, "fora_do_contrato": 0,
                             "rotulo_diferente": 0})

    def test_quem_saiu_ate_o_dia_7_fica_fora(self):
        r = ach.checar_alvo(self.b, rotulos(p1=1, p5=1))
        self.assertEqual((r["saiu_ate_o_dia_7"], r["fora_do_contrato"]), (1, 1))

    def test_turma_sem_resposta_fica_fora_mesmo_quem_ja_saiu(self):
        r = ach.checar_alvo(self.b, rotulos(p6=0, p7=0, p8=1))
        self.assertEqual((r["depois_de_2026_01_01"], r["fora_do_contrato"], r["rotulo_diferente"]), (2, 2, 0))

    def test_rotulo_trocado_aparece(self):
        r = ach.checar_alvo(self.b, rotulos(p2=1, p3=0, p4=1))
        self.assertEqual((r["fora_do_contrato"], r["rotulo_diferente"]), (0, 3))


# --------------------------------------------------------------------------- divisão

class Divisao(unittest.TestCase):
    b = base(pessoa(1, "2025-01-10"), pessoa(2, "2025-06-30"), pessoa(3, "2025-07-01"), pessoa(4, "2025-09-30"),
             pessoa(5, "2025-11-03"), pessoa(6, "2026-02-02"))

    def test_por_data_passa(self):
        self.assertEqual(ach.checar_divisao(self.b, [1, 2], [3, 4]),
                         {"treino_depois_do_inicio": 0, "teste_no_treino": 0})

    def test_treino_misturado_aparece(self):
        r = ach.checar_divisao(self.b, [1, 4], [2, 3])
        self.assertEqual(r["treino_depois_do_inicio"], 1)

    def test_teste_no_treino_e_so_outubro_a_janeiro(self):
        r = ach.checar_divisao(self.b, [1, 5, 6], [2, 3])
        self.assertEqual(r, {"treino_depois_do_inicio": 2, "teste_no_treino": 1})


# --------------------------------------------------------------------------- transformação

ADMISSOES = [pd.Timestamp(f"2025-0{1 + i % 6}-1{i % 9}") for i in range(1, 13)]
PEQUENA = base(*[pessoa(i, adm, (adm + pd.Timedelta(days=60)).date().isoformat() if i % 3 == 0 else None,
                        loja="L0" + str(1 + i % 2), salario=1800 + 50 * i, distancia=2.0 + i)
                 for i, adm in enumerate(ADMISSOES, start=1)])


def _partes(b):
    treino = b[b["data_admissao"] <= "2025-03-31"]
    medida = b[b["data_admissao"] > "2025-03-31"]
    return treino, medida


def _saida(x, b, treino, medida):
    x.index = b["id_pessoa"].to_numpy()
    y = pd.Series(b["saiu_180d"].fillna(0).to_numpy(), index=x.index)
    tr, me = treino["id_pessoa"].to_numpy(), medida["id_pessoa"].to_numpy()
    return x.loc[tr], y.loc[tr], x.loc[me], y.loc[me]


def escala_do_treino(b):
    treino, medida = _partes(b)
    x = (b[["distancia_km"]] - treino["distancia_km"].mean()) / treino["distancia_km"].std(ddof=0)
    return _saida(x, b, treino, medida)


def escala_da_base_inteira(b):
    treino, medida = _partes(b)
    x = (b[["distancia_km"]] - b["distancia_km"].mean()) / b["distancia_km"].std(ddof=0)
    return _saida(x, b, treino, medida)


def taxa_do_treino(b):
    treino, medida = _partes(b)
    taxa = treino.groupby("loja")["saiu_180d"].mean()
    x = pd.DataFrame({"taxa": b["loja"].map(taxa).fillna(treino["saiu_180d"].mean()).to_numpy()})
    return _saida(x, b, treino, medida)


def taxa_da_base_inteira(b):
    treino, medida = _partes(b)
    x = pd.DataFrame({"taxa": b.groupby("loja")["saiu_180d"].transform("mean").to_numpy()})
    return _saida(x, b, treino, medida)


class Transformacao(unittest.TestCase):
    def test_escala_do_treino_passa(self):
        self.assertEqual(ach.checar_transformacao(PEQUENA, escala_do_treino),
                         {"treino_com_resultado": 0, "medida_com_resultado": 0, "treino_com_distancia": 0})

    def test_taxa_ajustada_no_treino_passa(self):
        r = ach.checar_transformacao(PEQUENA, taxa_do_treino)
        self.assertEqual((r["treino_com_resultado"], r["medida_com_resultado"]), (0, 0))

    def test_escala_da_base_inteira_aparece(self):
        r = ach.checar_transformacao(PEQUENA, escala_da_base_inteira)
        self.assertGreater(r["treino_com_distancia"], 0)
        self.assertEqual(r["treino_com_resultado"], 0)

    def test_taxa_com_o_resultado_da_medida_aparece(self):
        r = ach.checar_transformacao(PEQUENA, taxa_da_base_inteira)
        self.assertGreater(r["treino_com_resultado"], 0)
        self.assertGreater(r["medida_com_resultado"], 0)


# --------------------------------------------------------------------------- os três projetos

class NosProjetos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import auditar_rh
        cls.base = auditar_rh.ler()
        cls.pipelines = auditar_rh.PIPELINES

    def perguntas(self, nome):
        p = self.pipelines[nome]
        x_tr, y_tr, x_me, y_me = p(self.base)
        return (ach.checar_alvo(self.base, pd.concat([y_tr, y_me])),
                ach.checar_divisao(self.base, x_tr.index, x_me.index),
                ach.checar_transformacao(self.base, p))

    def test_as_tres_perguntas_acham_os_defeitos_da_consultoria(self):
        alvo, divisao, transf = self.perguntas("consultoria")
        self.assertGreater(alvo["fora_do_contrato"], 0)
        self.assertGreater(divisao["treino_depois_do_inicio"], 0)
        self.assertGreater(transf["treino_com_resultado"], 0)

    def test_nada_no_pipeline_da_aula_09(self):
        for r in self.perguntas("pipeline da aula 09"):
            self.assertEqual(set(r.values()), {0}, r)

    def test_seu_conserto_passa_nas_tres_e_mede_na_validacao(self):
        for r in self.perguntas("consertar_rh"):
            self.assertEqual(set(r.values()), {0}, r)
        _, _, x_me, _ = self.pipelines["consertar_rh"](self.base)
        _, _, x_ref, _ = self.pipelines["pipeline da aula 09"](self.base)
        self.assertEqual(sorted(x_me.index), sorted(x_ref.index))


if __name__ == "__main__":
    unittest.main()
