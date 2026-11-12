"""As estratégias para a classe rara da aula «Comparar estratégias». Todas mexem só no treino.

Cada estratégia recebe o treino já preparado (x, y) e o número do sorteio, e retorna
(x, y, pesos): as linhas que o classificador vai ver e o peso de cada uma (None = peso 1).

    nenhuma          o treino como está
    peso de classe   o treino como está, com peso n / (2 × n da classe), o "balanced" do scikit-learn
    subamostragem    todos os cancelados e o mesmo número de entregues, sorteados
    sobreamostragem  todos os pedidos e cancelados repetidos, sorteados, até empatar
    SMOTE            todos os pedidos e cancelados novos, inventados entre dois cancelados vizinhos

Quem chama nunca passa a validação ou o teste para uma estratégia: eles ficam como chegaram.

treinar(x, y, pesos) usa o classificador da aula 10. Com pesos, ele faz a mesma conta com cada
linha multiplicada pelo seu peso; com todos os pesos iguais a 1, dá o mesmo modelo.

corrigir_nota(nota, vista, real) devolve a nota à proporção real do treino. Um modelo que viu
50% de cancelados dá notas altas demais para pedidos em que só uns 20% cancelam.
"""
import numpy as np
import pandas as pd

import classificador

VIZINHOS = 5


def sorteador(sorteio):
    """O gerador de números da NumPy com o bit generator escrito, não o padrão do default_rng."""
    return np.random.Generator(np.random.PCG64(sorteio))


def _checar(x, y):
    if len(x) != len(y):
        raise ValueError(f"x tem {len(x)} linhas e y tem {len(y)}")
    y = np.asarray(y).astype(int)
    if not ((y == 0) | (y == 1)).all():
        raise ValueError("y só pode ter 0 e 1")
    return y


def nenhuma(x, y, sorteio):
    _checar(x, y)
    return x, y, None


def peso_de_classe(x, y, sorteio):
    yy = _checar(x, y)
    n, n1 = len(yy), int(yy.sum())
    pesos = np.where(yy == 1, n / (2 * n1), n / (2 * (n - n1)))
    return x, y, pesos


def subamostragem(x, y, sorteio):
    yy = _checar(x, y)
    um, zero = np.flatnonzero(yy == 1), np.flatnonzero(yy == 0)
    fica = sorteador(sorteio).choice(zero, size=len(um), replace=False)
    i = np.r_[um, np.sort(fica)]
    return x.iloc[i], y.iloc[i], None


def sobreamostragem(x, y, sorteio):
    yy = _checar(x, y)
    um, zero = np.flatnonzero(yy == 1), np.flatnonzero(yy == 0)
    extra = sorteador(sorteio).choice(um, size=len(zero) - len(um), replace=True)
    i = np.r_[np.arange(len(yy)), extra]
    return x.iloc[i], y.iloc[i], None


def smote(x, y, sorteio, vizinhos=VIZINHOS):
    yy = _checar(x, y)
    raros = x.to_numpy(dtype=float)[yy == 1]
    faltam = int((yy == 0).sum() - (yy == 1).sum())
    dist = ((raros[:, None, :] - raros[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(dist, np.inf)
    perto = np.argsort(dist, axis=1, kind="stable")[:, :vizinhos]
    rng = sorteador(sorteio)
    de = rng.integers(0, len(raros), faltam)
    para = perto[de, rng.integers(0, vizinhos, faltam)]
    passo = rng.random(faltam)[:, None]
    novos = raros[de] + passo * (raros[para] - raros[de])
    xn = pd.concat([x, pd.DataFrame(novos, columns=x.columns)], ignore_index=True)
    yn = pd.concat([pd.Series(np.asarray(y)), pd.Series(np.ones(faltam, dtype=int))], ignore_index=True)
    return xn, yn, None


ESTRATEGIAS = {
    "nenhuma": nenhuma,
    "peso de classe": peso_de_classe,
    "subamostragem": subamostragem,
    "sobreamostragem": sobreamostragem,
    "SMOTE": smote,
}
SORTEIAM = ["subamostragem", "sobreamostragem", "SMOTE"]


def treinar(x, y, pesos=None):
    """O classificador da aula 10. Com pesos, cada linha conta na conta com o seu peso."""
    if pesos is None:
        return classificador.treinar(x, y)
    m = np.c_[np.ones(len(x)), np.asarray(x, dtype=float)]
    yy = np.asarray(y, dtype=float)
    w = np.asarray(pesos, dtype=float)
    coef = np.zeros(m.shape[1])
    pen = np.eye(m.shape[1]) * classificador.PENALIDADE
    pen[0, 0] = 0
    with np.errstate(all="ignore"):
        for _ in range(classificador.PASSOS):
            p = 1 / (1 + np.exp(-(m @ coef)))
            grad = m.T @ (w * (p - yy)) + pen @ coef
            hess = m.T @ (m * (w * p * (1 - p))[:, None]) + pen
            coef = coef - np.linalg.solve(hess, grad)
    return {"colunas": list(x.columns), "pesos": coef}


def proporcao(y, pesos=None):
    """A parte de cancelados que o classificador viu no treino, contando o peso de cada linha."""
    yy = np.asarray(y, dtype=float)
    w = np.ones(len(yy)) if pesos is None else np.asarray(pesos, dtype=float)
    return float((w * yy).sum() / w.sum())


def corrigir_nota(nota, vista, real):
    """Leva a nota de um modelo que viu a proporção `vista` para a proporção `real`.

    A chance de cancelar (nota / (1 - nota)) é multiplicada pela razão entre as duas chances
    da classe. Com vista igual a real, a nota não muda.
    """
    if not (0 < vista < 1 and 0 < real < 1):
        raise ValueError("as proporções precisam estar entre 0 e 1")
    razao = (real / (1 - real)) / (vista / (1 - vista))
    nota = np.asarray(nota, dtype=float)
    chance = nota / (1 - nota) * razao
    return chance / (1 + chance)
