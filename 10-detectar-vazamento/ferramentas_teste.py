"""Duas peças usadas pelos testes da aula «Detectar vazamento»: comparar tabelas e mostrar o resultado."""
import unittest

import numpy as np


def iguais(a, b):
    """Mesmas colunas, mesmas linhas, mesmos números (vazio igual a vazio)."""
    return (list(a.columns) == list(b.columns) and list(a.index) == list(b.index)
            and np.allclose(a.to_numpy(float), b.to_numpy(float), equal_nan=True))


def rodar(caso):
    """Roda os testes e mostra uma linha por teste, com o motivo de cada falha. Retorna 1 se algum falhou."""
    testes = list(unittest.defaultTestLoader.loadTestsFromTestCase(caso))
    resultado = unittest.TestResult()
    unittest.TestSuite(testes).run(resultado)
    motivo = {}
    for teste, texto in resultado.failures:
        motivo[teste.id()] = texto.strip().splitlines()[-1].split(" : ", 1)[-1]
    for teste, texto in resultado.errors:
        motivo[teste.id()] = "erro: " + texto.strip().splitlines()[-1]
    for teste in testes:
        nome = teste.id().split(".")[-1]
        print(f"  {'FALHOU' if teste.id() in motivo else 'ok    '} {nome}")
        if teste.id() in motivo:
            print(f"         {motivo[teste.id()]}")
    print(f"{len(testes) - len(motivo)} de {len(testes)} testes passaram")
    return 1 if motivo else 0
