"""O exercício da aula «Auditar estabilidade por segmento».

A auditoria da lista de ligações por categoria, forma de pagamento e canal.

    python3 auditoria_pedidos.py            # o relatório, depois que você escrever as três funções
    python3 testar_auditoria_pedidos.py     # os testes das suas funções

A parte pronta separa os pedidos como na aula 05 (treino de janeiro a março de 2026, validação em
abril e maio), prepara como na aula 10, treina o classificador pronto e dá a nota de cada pedido da
validação. Junho é o teste e fica fechado. A regra liga quando a nota passa do empate, 0,333.

Você escreve três funções: economia(), por_recorte() e embaralhar_recortes().
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LIGACAO = 5               # R$ de uma ligação
CANCELAMENTO = 15         # R$ de um cancelamento que passa sem ligação
EMPATE = LIGACAO / CANCELAMENTO     # 0,333
COLUNAS = ["categoria", "forma_pagamento", "canal"]
PASTA = "15-auditar-estabilidade-por-segmento"


def carregar():
    """Pronto. Retorna (treino, v): os pedidos do treino e a validação com cancelado e nota."""
    if not Path("pipeline_corrigido.py").is_file() or not Path("../dados/loja/pedidos_export_completo.csv").is_file():
        sys.exit(f"não achei os arquivos. Rode de dentro da pasta {PASTA} do kit.")
    import classificador
    import pipeline_corrigido as pc
    base = pd.read_csv("../dados/loja/pedidos_export_completo.csv", parse_dates=["data_pedido"])
    x_tr, y_tr, x_va, y_va = pc.preparar(base)
    modelo = classificador.treinar(x_tr, y_tr)
    pedidos = base.set_index("id_pedido")
    treino = pedidos.loc[x_tr.index, COLUNAS + ["cancelado"]]
    v = pedidos.loc[x_va.index, COLUNAS + ["cancelado"]].copy()
    v["nota"] = classificador.nota(modelo, x_va).to_numpy()
    return treino, v


def economia(y, nota):
    """Em reais, contra não ligar para ninguém, nos mesmos pedidos.

    y: 1 para pedido cancelado, 0 para entregue. nota: a nota de cada pedido.
    A lista liga quando a nota passa de EMPATE. Cada ligação custa LIGACAO; cada cancelamento que
    passa sem ligação custa CANCELAMENTO. Não ligar para ninguém custa CANCELAMENTO por cancelado.
    Retorna um número (int ou float).
    """
    raise NotImplementedError("escreva a economia(): veja o docstring")


def por_recorte(v, coluna, valores):
    """Uma linha para cada valor de `valores`, na mesma ordem, inclusive os que não têm pedido em v.

    v: tabela com a coluna, `cancelado` e `nota`, um pedido por linha.
    Retorna uma lista de dicionários com:
      valor, pedidos, cancelados, ligacoes
      economia     economia() nos pedidos do recorte; None quando o recorte não tem pedido
      faixa        (baixo, alto) de segmentos.faixa(economia, [cancelado, nota]), só com os
                   pedidos do recorte, com os sorteios e o sorteio padrão do segmentos.py
      leitura      segmentos.leitura(baixo, alto)
    """
    raise NotImplementedError("escreva a por_recorte(): veja o docstring")


def embaralhar_recortes(v, colunas, vezes=1000, sorteio=15):
    """O melhor e o pior recorte, em economia, quando as notas trocam de lugar entre os pedidos.

    Entram todos os valores com pedido em v de todas as `colunas`. Usa segmentos.embaralhar com
    `vezes` e `sorteio`. Retorna (melhores, piores), duas listas com `vezes` números.
    """
    raise NotImplementedError("escreva a embaralhar_recortes(): veja o docstring")


# ---------------------------------------------------------------- pronto: o relatório

def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    if x is None:
        return "-"
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def de_a(par):
    return "-" if par[0] is None else f"{reais(par[0])} a {reais(par[1])}"


def main():
    import segmentos
    treino, v = carregar()
    y, nota = v["cancelado"].to_numpy(), v["nota"].to_numpy()
    print(f"validação: {len(v)} pedidos de abril e maio de 2026, {int(y.sum())} cancelados ({pct(y.mean())}); "
          f"junho, o teste, fica fechado")
    print(f"regra: liga quando a nota passa de 0,333; ligação R$ {LIGACAO}, cancelamento R$ {CANCELAMENTO}")
    todos = por_recorte(v.assign(todos="todos"), "todos", ["todos"])[0]
    print(f"todos os pedidos: {todos['ligacoes']} ligações, economia {reais(todos['economia'])}, "
          f"faixa {de_a(todos['faixa'])}")
    print(f"faixas: {segmentos.SORTEIOS} sorteios com reposição dentro de cada recorte, sorteio "
          f"{segmentos.SORTEIO}; tira 2,5% de cada lado")

    print("\n1. a lista em cada recorte")
    print(f"{'recorte':<26}{'treino':>7}{'pedidos':>8}{'cancelados':>11}{'ligações':>9}{'economia':>10}"
          f"{'faixa da economia':>22}  leitura")
    medidas = []
    for c in COLUNAS:
        valores = sorted(set(treino[c]) | set(v[c]))
        for r in por_recorte(v, c, valores):
            medidas.append((c, r))
            print(f"{c + ' ' + str(r['valor']):<26}{int((treino[c] == r['valor']).sum()):>7}{r['pedidos']:>8}"
                  f"{r['cancelados']:>11}{r['ligacoes']:>9}{reais(r['economia']):>10}{de_a(r['faixa']):>22}"
                  f"  {r['leitura']}")
    com = [(c, r) for c, r in medidas if r["economia"] is not None]
    melhor = max(com, key=lambda t: t[1]["economia"])
    pior = min(com, key=lambda t: t[1]["economia"])
    melhores, piores = map(np.asarray, embaralhar_recortes(v, COLUNAS))
    print(f"\n2. as notas embaralhadas entre os {len(v)} pedidos, {len(melhores)} vezes, nos {len(com)} recortes")
    print(f"   o melhor recorte de verdade: {melhor[0]} {melhor[1]['valor']}, {reais(melhor[1]['economia'])}; "
          f"o pior: {pior[0]} {pior[1]['valor']}, {reais(pior[1]['economia'])}")
    print(f"   melhor recorte com as notas embaralhadas: mediana {reais(float(np.median(melhores)))}; "
          f"chega a {reais(melhor[1]['economia'])} em {pct((melhores >= melhor[1]['economia']).mean())}")
    print(f"   pior recorte com as notas embaralhadas: mediana {reais(float(np.median(piores)))}; "
          f"chega a {reais(pior[1]['economia'])} em {pct((piores <= pior[1]['economia']).mean())}")


if __name__ == "__main__":
    main()
