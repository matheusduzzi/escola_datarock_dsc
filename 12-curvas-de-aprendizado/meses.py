"""Pedidos mais recentes ou mais pedidos? Três treinos, todos medidos nos pedidos de maio.

Aula «Curvas de aprendizado» do curso ML: preparação e validação. Rode de dentro dessa pasta:

    python3 meses.py

O ajustar da aula 10 recusa pedido depois de março. Aqui o fim do treino vai até abril de propósito,
e maio fica fora de todo ajuste. Junho, o teste, não é lido.
"""
import pandas as pd

import classificador as clf
import pipeline_corrigido as pc

pc.FIM_TREINO = "2026-04-30"
e = pd.read_csv("../dados/loja/pedidos_export_completo.csv", parse_dates=["data_pedido"])
maio = e[e["data_pedido"].dt.month == 5]
for nome, inicio, fim in [("janeiro a março", "2026-01-01", "2026-03-31"),
                          ("fevereiro a abril", "2026-02-01", "2026-04-30"),
                          ("janeiro a abril", "2026-01-01", "2026-04-30")]:
    t = e[(e["data_pedido"] >= inicio) & (e["data_pedido"] <= fim)]
    p = pc.ajustar(t)
    m = clf.treinar(pc.aplicar(p, t), t["cancelado"])
    a = clf.acerto_do_par(clf.nota(m, pc.aplicar(p, maio)), maio["cancelado"])
    print(f"treino de {nome}: {len(t)} pedidos; acerto do par em maio: {clf.pct(a)}")
