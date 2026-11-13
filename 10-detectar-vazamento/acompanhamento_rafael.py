"""A preparação do Rafael para a lista do dia 7. É a base do exercício: ela tem vazamentos.

Aula «Detectar vazamento» do curso ML: preparação e validação. Rode de dentro da pasta da aula:

    python3 acompanhamento_rafael.py

preparar(base) recebe as 1500 admissões e retorna x_treino, y_treino, x_validacao, y_validacao.
As linhas são as do contrato do alvo da aula 03 (admitidas até 2026-01-01, sem quem saiu nos
primeiros 7 dias). Treino: admitidas até 2025-06-30; validação: de julho a setembro de 2025.
A lista roda no dia 7 depois da admissão, para quem já foi contratado.
"""
import sys
from pathlib import Path

import pandas as pd

from classificador import acerto_do_par, nota, pct, treinar

BASE = Path("../dados/pessoas/admissoes.csv")
FIM_TREINO = pd.Timestamp("2025-06-30")
FIM_VALIDACAO = pd.Timestamp("2025-09-30")
FIM_CONTRATO = pd.Timestamp("2026-01-01")
NUMERICAS = ["salario_base", "distancia_km", "indicacao", "horas_treinamento"]
CATEGORIAS = ["loja", "cargo", "turno"]


def equipe(a):
    return a["loja"] + " " + a["cargo"] + " " + a["turno"]


def preparar(base):
    a = base.copy()
    a["distancia_km"] = a["distancia_km"].fillna(a["distancia_km"].median())
    x = (a[NUMERICAS] - a[NUMERICAS].mean()) / a[NUMERICAS].std(ddof=0)
    for c in CATEGORIAS:
        for v in sorted(a[c].unique()):
            x[f"{c}_{v}"] = (a[c] == v).astype(float)
    com_resposta = a[a["saiu_180d"].notna()]
    taxa = com_resposta.groupby(equipe(com_resposta))["saiu_180d"].mean()
    x["taxa_equipe"] = equipe(a).map(taxa).fillna(com_resposta["saiu_180d"].mean())
    x.index = a["id_pessoa"].to_numpy()

    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    contrato = ((a["data_admissao"] <= FIM_CONTRATO) & ~(dias <= 7)).to_numpy()
    adm = a["data_admissao"].to_numpy()
    tr = contrato & (adm <= FIM_TREINO)
    va = contrato & (adm > FIM_TREINO) & (adm <= FIM_VALIDACAO)
    y = pd.Series(a["saiu_180d"].to_numpy(), index=x.index)
    return x[tr], y[tr], x[va], y[va]


def carregar():
    if not BASE.exists():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 10-detectar-vazamento do kit.")
    return pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])


def main(prep=preparar):
    x_tr, y_tr, x_va, y_va = prep(carregar())
    modelo = treinar(x_tr, y_tr)
    print(f"treino: {len(x_tr)} pessoas; validação: {len(x_va)}; colunas: {x_tr.shape[1]}")
    print(f"acerto do par: {pct(acerto_do_par(nota(modelo, x_tr), y_tr))} no treino, "
          f"{pct(acerto_do_par(nota(modelo, x_va), y_va))} na validação")


if __name__ == "__main__":
    main()
