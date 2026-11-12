"""Modelo do acompanhamento no primeiro mês. Entrega da consultoria, versão de 20/07/2026.

    python3 consultoria_acompanhamento.py

preparar(base) recebe as admissões e retorna x_treino, y_treino, x_teste e y_teste, com o id da
pessoa no índice. O modelo é o classificador que a loja já usa (classificador.py). O corte é o
do RH: 0,32.
"""
import sys
from pathlib import Path

import pandas as pd

from classificador import acerto_do_par, nota, pct, treinar

BASE = Path("../dados/pessoas/admissoes.csv")
CORTE = 0.32
NUMERICAS = ["salario_base", "distancia_km", "indicacao"]
CATEGORIAS = ["loja", "cargo", "turno"]


def preparar(base):
    a = base.reset_index(drop=True).copy()

    # Rótulo: a coluna saiu_180d da base. Vazia quer dizer que a pessoa não saiu.
    a["rotulo"] = a["saiu_180d"].fillna(0).astype(int)

    # Distância vazia vira a mediana; escala das colunas de número; uma coluna por categoria.
    a["distancia_km"] = a["distancia_km"].fillna(a["distancia_km"].median())
    x = (a[NUMERICAS] - a[NUMERICAS].mean()) / a[NUMERICAS].std(ddof=0)
    for c in CATEGORIAS:
        for v in sorted(a[c].unique()):
            x[f"{c}_{v}"] = (a[c] == v).astype(float)

    # Coluna nova: a taxa de saída da equipe (loja e cargo).
    x["taxa_equipe"] = a.groupby(a["loja"] + " " + a["cargo"])["rotulo"].transform("mean")

    x.index = a["id_pessoa"].to_numpy()
    y = pd.Series(a["rotulo"].to_numpy(), index=x.index)

    # Teste: 30% das pessoas, sorteadas. O sorteio é fixo para dar o mesmo resultado sempre.
    teste = a.sample(frac=0.3, random_state=17)["id_pessoa"].to_numpy()
    no_teste = x.index.isin(teste)
    return x[~no_teste], y[~no_teste], x[no_teste], y[no_teste]


def main():
    if not BASE.is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 17-auditoria-de-um-pipeline do kit.")
    x_tr, y_tr, x_te, y_te = preparar(pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"]))
    s = nota(treinar(x_tr, y_tr), x_te)
    lista = s > CORTE
    certas = int((lista & (y_te == 1)).sum())
    print(f"treino: {len(x_tr)} pessoas; teste: {len(x_te)} pessoas, {int(y_te.sum())} saíram")
    print(f"lista com corte 0,32: {int(lista.sum())} pessoas, {certas} certas")
    print(f"acerto do par {pct(acerto_do_par(s, y_te))}")


if __name__ == "__main__":
    main()
