"""As peças da auditoria por recorte, da aula «Auditar estabilidade por segmento».

faixa(medida, colunas, sorteios, sorteio): sorteia de novo as linhas de um recorte, com
reposição, `sorteios` vezes, e mede cada sorteio. Retorna o valor mais baixo e o mais alto
depois de tirar os 2,5% de baixo e os 2,5% de cima. Com 1000 sorteios, tira 25 de cada lado.
Esse jeito de medir a dúvida tem nome: bootstrap.

leitura(baixo, alto): o que a faixa permite dizer de um saldo ou de uma economia.

embaralhar(notas, recortes, medida, vezes, sorteio): troca as notas de lugar entre as pessoas
(ou os pedidos), mede cada recorte e guarda o melhor e o pior. É o que um modelo sem nenhuma
informação acharia, só de olhar muitos recortes.
"""
import numpy as np

SORTEIOS = 1000
SORTEIO = 15


def gerador(sorteio):
    """O mesmo sorteio dá os mesmos números na mesma versão do NumPy."""
    return np.random.Generator(np.random.PCG64(sorteio))


def faixa(medida, colunas, sorteios=SORTEIOS, sorteio=SORTEIO):
    """Faixa de 95% de `medida` em `sorteios` sorteios com reposição das linhas.

    medida: função que recebe os arrays de `colunas`, já sorteados, e retorna um número ou None.
    colunas: lista de arrays do mesmo tamanho, uma linha por pessoa ou pedido do recorte.
    Retorna (baixo, alto, validos). Sorteio em que a medida retorna None fica fora e não conta em
    `validos`. Com menos de 40 sorteios válidos, retorna (None, None, validos).
    """
    colunas = [np.asarray(c) for c in colunas]
    n = len(colunas[0])
    if any(len(c) != n for c in colunas):
        raise ValueError("as colunas do recorte têm tamanhos diferentes")
    if n == 0:
        return None, None, 0
    g = gerador(sorteio)
    valores = []
    for _ in range(sorteios):
        i = g.integers(0, n, n)
        v = medida(*[c[i] for c in colunas])
        if v is not None:
            valores.append(v)
    if len(valores) < 40:
        return None, None, len(valores)
    valores = np.sort(np.asarray(valores, dtype=float))
    corte = int(len(valores) * 0.025)
    return float(valores[corte]), float(valores[len(valores) - 1 - corte]), len(valores)


def leitura(baixo, alto):
    """ganha, perde, não dá para dizer ou sem medida."""
    if baixo is None or alto is None:
        return "sem medida"
    if baixo > 0:
        return "ganha"
    if alto < 0:
        return "perde"
    return "não dá para dizer"


def embaralhar(notas, recortes, medida, vezes=SORTEIOS, sorteio=SORTEIO):
    """O melhor e o pior recorte quando as notas trocam de lugar ao acaso.

    notas: array com a nota de cada linha.
    recortes: lista de arrays de True/False, um por recorte, com o mesmo tamanho de `notas`.
    medida: função que recebe (notas do recorte, máscara do recorte) e retorna um número.
    Retorna (melhores, piores): duas listas com `vezes` números cada.
    """
    notas = np.asarray(notas, dtype=float)
    g = gerador(sorteio)
    melhores, piores = [], []
    for _ in range(vezes):
        n = g.permutation(notas)
        valores = [medida(n[r], r) for r in recortes]
        melhores.append(max(valores))
        piores.append(min(valores))
    return melhores, piores
