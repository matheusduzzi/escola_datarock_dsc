"""O classificador pronto e as duas medidas da aula «Detectar vazamento».

treinar(x, y) ajusta uma regressão logística com uma penalidade pequena; nota(modelo, x) dá a
nota de 0 a 1 de cada linha. Como o classificador aprende por dentro fica para o curso
ML supervisionado. Aqui ele é a peça fixa: o que muda entre uma rodada e outra é a preparação.

acerto_do_par(nota, y): sorteando uma linha com y = 1 e uma com y = 0, em quantos pares a de
y = 1 tem nota maior. Empate vale meio. 50% é o acerto de uma moeda; 100% separa tudo.

varrer(base, alvo): o acerto do par de cada coluna sozinha, na direção que der mais.
"""
import numpy as np
import pandas as pd

PENALIDADE = 1.0
PASSOS = 30


def treinar(x, y):
    """Regressão logística pelo método de Newton. Mesma entrada, mesmo modelo, toda vez."""
    m = np.c_[np.ones(len(x)), np.asarray(x, dtype=float)]
    y = np.asarray(y, dtype=float)
    pesos = np.zeros(m.shape[1])
    pen = np.eye(m.shape[1]) * PENALIDADE
    pen[0, 0] = 0
    with np.errstate(all="ignore"):
        for _ in range(PASSOS):
            p = 1 / (1 + np.exp(-(m @ pesos)))
            grad = m.T @ (p - y) + pen @ pesos
            hess = m.T @ (m * (p * (1 - p))[:, None]) + pen
            pesos = pesos - np.linalg.solve(hess, grad)
    return {"colunas": list(x.columns), "pesos": pesos}


def nota(modelo, x):
    if list(x.columns) != modelo["colunas"]:
        raise ValueError("as colunas não são as do treino do modelo")
    m = np.c_[np.ones(len(x)), np.asarray(x, dtype=float)]
    with np.errstate(all="ignore"):
        return pd.Series(1 / (1 + np.exp(-(m @ modelo["pesos"]))), index=x.index)


def acerto_do_par(nota, y):
    nota = pd.Series(np.asarray(nota, dtype=float))
    y = np.asarray(y)
    posto = nota.rank().to_numpy()
    n1 = int((y == 1).sum())
    n0 = len(y) - n1
    return float((posto[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def varrer(base, alvo, pular=()):
    """Acerto do par de cada coluna sozinha. Texto entra pela taxa do alvo de cada categoria."""
    y = base[alvo]
    resultado = {}
    for coluna in base.columns:
        if coluna == alvo or coluna in pular:
            continue
        x = base[coluna]
        if not pd.api.types.is_numeric_dtype(x):
            x = y.groupby(x).transform("mean")
        a = acerto_do_par(x.fillna(x.median()), y)
        resultado[coluna] = max(a, 1 - a)
    return pd.Series(resultado).sort_values(ascending=False)


def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return num(100 * x) + "%"
