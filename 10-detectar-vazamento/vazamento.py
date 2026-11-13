"""A demonstração da aula «Detectar vazamento», do curso ML: preparação e validação.

Rode de dentro da pasta da aula:

    python3 vazamento.py

Lê o export completo dos pedidos, mede a preparação do Rafael e a corrigida com o mesmo
classificador e desmonta os dois vazamentos, um de cada vez. O bloco 6 mostra a versão do Rafael na hora do
pedido, quando as colunas gravadas depois ainda valem 0. Treino: janeiro a março de 2026;
validação: abril e maio. Junho é o teste: nenhuma conta desse programa mede nada em junho.
"""
import sys
from pathlib import Path

import pandas as pd

import pipeline_corrigido
import pipeline_rafael
from classificador import acerto_do_par, nota, num, pct, treinar, varrer

BASE = Path("../dados/loja/pedidos_export_completo.csv")
FIM_TREINO = pd.Timestamp("2026-03-31")
FIM_VALIDACAO = pd.Timestamp("2026-05-31")
HONESTAS = ["valor", "prazo_prometido_dias", "pedidos_anteriores", "cliente_novo"]
DEPOIS = ["dias_ate_entrega", "contatos_sac"]
CATEGORIAS = ["categoria", "forma_pagamento", "canal"]


def variante(e, depois, taxa, ajuste):
    """A preparação com cada defeito ligado ou desligado. ajuste: "base inteira" ou "treino"."""
    numericas = HONESTAS + (DEPOIS if depois else [])
    tr = e["data_pedido"] <= FIM_TREINO
    va = (e["data_pedido"] > FIM_TREINO) & (e["data_pedido"] <= FIM_VALIDACAO)
    fonte = e if ajuste == "base inteira" else e[tr]
    x = (e[numericas] - fonte[numericas].mean()) / fonte[numericas].std(ddof=0)
    for c in CATEGORIAS:
        for v in sorted(fonte[c].unique()):
            x[f"{c}_{v}"] = (e[c] == v).astype(float)
    if taxa:
        t = fonte.groupby(pipeline_rafael.combinacao(fonte))["cancelado"].mean()
        x["taxa_combinacao"] = pipeline_rafael.combinacao(e).map(t).fillna(fonte["cancelado"].mean())
    x.index = e["id_pedido"].to_numpy()
    y = pd.Series(e["cancelado"].to_numpy(), index=x.index)
    return x[tr.to_numpy()], y[tr.to_numpy()], x[va.to_numpy()], y[va.to_numpy()]


def medir(prep):
    x_tr, y_tr, x_va, y_va = prep
    modelo = treinar(x_tr, y_tr)
    return acerto_do_par(nota(modelo, x_tr), y_tr), acerto_do_par(nota(modelo, x_va), y_va), x_tr.shape[1]


def iguais(a, b):
    return all(x.equals(y) for x, y in zip(a, b))


def main():
    if not BASE.exists():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 10-detectar-vazamento do kit.")
    e = pd.read_csv(BASE, parse_dates=["data_pedido"])
    tr = e[e["data_pedido"] <= FIM_TREINO]
    va = e[(e["data_pedido"] > FIM_TREINO) & (e["data_pedido"] <= FIM_VALIDACAO)]
    print(f"pedidos: {len(e)}; treino até {FIM_TREINO.date()} ({len(tr)}); "
          f"validação até {FIM_VALIDACAO.date()} ({len(va)}); junho, o teste: {len(e) - len(tr) - len(va)}")
    print("acerto do par: sorteando um pedido cancelado e um entregue, em quantos pares o cancelado tem nota maior")

    print("\n1. as duas preparações, com o mesmo classificador")
    raf = pipeline_rafael.preparar(e.copy())
    cor = pipeline_corrigido.preparar(e.copy())
    print(f"  {'preparação':<24}{'colunas':>8}{'no treino':>11}{'na validação':>14}")
    for rotulo, prep in [("a do Rafael", raf), ("a corrigida", cor)]:
        a_tr, a_va, n = medir(prep)
        print(f"  {rotulo:<24}{n:>8}{pct(a_tr):>11}{pct(a_va):>14}")

    print("\n2. cada coluna sozinha no treino, a varredura")
    aucs = varrer(tr, "cancelado", pular=("id_pedido", "data_pedido"))
    for coluna, a in aucs.items():
        marca = "  <- nasce depois do pedido" if coluna in DEPOIS else ""
        print(f"  {coluna:<22}{pct(a):>7}{marca}")

    print("\n3. um defeito por vez")
    casos = [
        ("as duas coisas (a do Rafael)", True, True, "base inteira"),
        ("sem as colunas de depois", False, True, "base inteira"),
        ("sem elas, taxa só do treino", False, True, "treino"),
        ("sem elas e sem a taxa (a corrigida)", False, False, "treino"),
        ("a corrigida, escala nos 2400", False, False, "base inteira"),
    ]
    print(f"  {'preparação':<38}{'no treino':>10}{'na validação':>14}")
    for rotulo, depois, taxa, ajuste in casos:
        a_tr, a_va, _ = medir(variante(e, depois, taxa, ajuste))
        print(f"  {rotulo:<38}{pct(a_tr):>10}{pct(a_va):>14}")
    print(f"  a primeira linha é a do pipeline_rafael.py: "
          f"{'sim' if iguais(variante(e, True, True, 'base inteira'), raf) else 'NÃO'}; "
          f"a quarta é a do pipeline_corrigido.py: "
          f"{'sim' if iguais(variante(e, False, False, 'treino'), cor) else 'NÃO'}")

    print("\n4. a taxa da combinação calculada nos 2400 pedidos")
    comb = pipeline_rafael.combinacao(e)
    vezes = comb.map(comb.value_counts())
    so_ele = va.index[vezes[va.index] == 1]
    print(f"  combinações de categoria, pagamento, canal, cliente novo e prazo: {comb[tr.index].nunique()} no treino, "
          f"{comb.nunique()} nos 2400")
    print(f"  pedidos da validação cuja combinação só aparece nele mesmo: {len(so_ele)} de {len(va)}; "
          f"a taxa deles é a própria resposta: {'sim' if (raf[2].loc[va.loc[so_ele, 'id_pedido'], 'taxa_combinacao'].to_numpy() == va.loc[so_ele, 'cancelado'].to_numpy()).all() else 'não'}")
    fora = int((~comb[va.index].isin(comb[tr.index])).sum())
    print(f"  pedidos da validação com combinação que o treino não tem: {fora} de {len(va)}")

    print("\n5. a escala nos 2400 pedidos")
    for c in ["valor", "prazo_prometido_dias"]:
        print(f"  {c}: treino tira {num(tr[c].mean(), 2)} e divide por {num(tr[c].std(ddof=0), 2)}; "
              f"2400 tira {num(e[c].mean(), 2)} e divide por {num(e[c].std(ddof=0), 2)}")
    _, a_va, _ = medir(variante(e, False, False, "treino"))
    _, b_va, _ = medir(variante(e, False, False, "base inteira"))
    print(f"  acerto do par na validação: {pct(a_va)} com a escala do treino, {pct(b_va)} com a dos 2400")

    print("\n6. a do Rafael na hora do pedido, quando as colunas de depois ainda são 0")
    modelo = treinar(raf[0], raf[1])
    hora = raf[2].copy()
    for c in DEPOIS:
        hora[c] = (0 - e[c].mean()) / e[c].std(ddof=0)
    cheia = (nota(modelo, raf[2]) > 0.5).mean()
    zero = (nota(modelo, hora) > 0.5).mean()
    print(f"  pedidos da validação com nota acima de 0,5: {pct(cheia)} com as colunas cheias, "
          f"{pct(zero)} com dias_ate_entrega e contatos_sac em 0; cancelaram de verdade: {pct(raf[3].mean())}")


if __name__ == "__main__":
    main()
