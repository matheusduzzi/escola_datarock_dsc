"""One-hot, ordinal e target encoding nas admissões, com todo número calculado no treino.

Aula «Encoding de categorias» do curso ML: preparação e validação.
Rode de dentro da pasta da aula:

    python3 encoding.py

Lê ../dados/pessoas/admissoes.csv, aplica o contrato do alvo da aula 03 e a divisão por data
(treino até 2025-06-30, validação até 2025-09-30, teste até 2026-01-01). As linhas do teste saem
logo depois da leitura: nenhuma conta usa o teste. As pessoas admitidas depois de 2026-01-01
fazem o papel das pessoas novas que a lista vai receber; delas o programa só lê as categorias.

A dobra de cada pessoa do treino é o resto da divisão do id_pessoa por 5. Assim a conta sai
igual toda vez, sem sorteio.
"""
import sys
from pathlib import Path

import pandas as pd

BASE = Path("../dados/pessoas/admissoes.csv")
FIM_TREINO = "2025-06-30"
FIM_VALIDACAO = "2025-09-30"
FIM_CONTRATO = "2026-01-01"
COLUNAS = ["loja", "cargo", "turno"]
DOBRAS = 5
SUAVIZACAO = 20


def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return num(100 * x) + "%"


def carregar():
    if not BASE.exists():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 08-encoding-de-categorias do kit.")
    a = pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])
    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    contrato = (a["data_admissao"] <= FIM_CONTRATO) & ~(dias <= 7)
    a["parte"] = "fora do contrato"
    a.loc[contrato, "parte"] = "teste"
    a.loc[contrato & (a["data_admissao"] <= FIM_VALIDACAO), "parte"] = "validação"
    a.loc[contrato & (a["data_admissao"] <= FIM_TREINO), "parte"] = "treino"
    a["equipe"] = a["loja"] + " " + a["cargo"] + " " + a["turno"]
    return a


def acerto_do_par(nota, saiu):
    """Em quantos pares (uma pessoa que saiu, uma que ficou) a que saiu tem nota maior. Empate vale meio."""
    posto = nota.rank()
    n1 = int(saiu.sum())
    n0 = len(saiu) - n1
    return (posto[saiu == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def media_por_categoria(base, coluna, m):
    """Taxa de saída de cada categoria, puxada para a taxa geral da base pelo peso de m pessoas."""
    geral = base["saiu_180d"].mean()
    g = base.groupby(coluna)["saiu_180d"].agg(["sum", "count"])
    return (g["sum"] + m * geral) / (g["count"] + m), geral


def fora_da_dobra(treino, coluna, m):
    """Nota de cada pessoa do treino calculada só com as outras quatro dobras."""
    nota = pd.Series(index=treino.index, dtype=float)
    dobra = treino["id_pessoa"] % DOBRAS
    sem_par = 0
    for k in range(DOBRAS):
        dentro = dobra == k
        mapa, geral = media_por_categoria(treino[~dentro], coluna, m)
        v = treino.loc[dentro, coluna].map(mapa)
        sem_par += int(v.isna().sum())
        nota[dentro] = v.fillna(geral)
    return nota, sem_par


def main():
    a = carregar()
    n = a["parte"].value_counts()
    print(f"admissões: {len(a)}; contrato da aula 03: {int(n.drop('fora do contrato').sum())} pessoas")
    print(f"treino: até {FIM_TREINO} ({n['treino']}); validação: até {FIM_VALIDACAO} ({n['validação']}); "
          f"teste: {n['teste']}, fechado")
    novas = a[a["data_admissao"] > FIM_CONTRATO]
    a = a[a["parte"] != "teste"]
    tr = a[a["parte"] == "treino"]
    va = a[a["parte"] == "validação"]
    print(f"pessoas novas, admitidas depois de {FIM_CONTRATO}: {len(novas)}")
    print("todo número do mapa sai do treino")

    print("\n1. categorias no treino e nas pessoas novas")
    print(f"  {'coluna':<8}{'no treino':>10}{'nas novas':>11}  o que o treino não tem")
    for col in COLUNAS + ["equipe"]:
        faltam = novas.loc[~novas[col].isin(tr[col]), col]
        if col == "equipe":
            txt = f"{faltam.nunique()} equipes, {len(faltam)} pessoas"
        else:
            txt = ", ".join(f"{c} ({k} pessoas)" for c, k in faltam.value_counts().items()) or "nada"
        print(f"  {col:<8}{tr[col].nunique():>10}{novas[col].nunique():>11}  {txt}")
    nova_cat = ~novas["loja"].isin(tr["loja"]) | ~novas["cargo"].isin(tr["cargo"])
    print(f"  pessoas novas com loja ou cargo que o treino não tem: {int(nova_cat.sum())} de {len(novas)}")
    tam = tr["equipe"].value_counts()
    print(f"  equipe = loja + cargo + turno; no treino, {int((tam < 5).sum())} das {len(tam)} equipes "
          f"têm menos de 5 pessoas")

    print("\n2. one-hot: uma coluna de 0 e 1 para cada categoria")
    x_tr = pd.get_dummies(tr[COLUNAS])
    x_novas = pd.get_dummies(novas[COLUNAS])
    a_mais = [c for c in x_novas.columns if c not in x_tr.columns]
    print(f"  get_dummies no treino: {x_tr.shape[1]} colunas")
    print(f"  get_dummies nas pessoas novas: {x_novas.shape[1]} colunas; a mais: {', '.join(a_mais)}")
    print(f"  get_dummies numa pessoa só: {pd.get_dummies(novas[COLUNAS].head(1)).shape[1]} colunas")
    fixo = x_novas.reindex(columns=x_tr.columns, fill_value=False)
    sem = {c: int((~fixo.filter(like=f"{c}_").any(axis=1)).sum()) for c in COLUNAS}
    print(f"  com as colunas do treino: {fixo.shape[1]} colunas; pessoas novas com todas as colunas zeradas: "
          f"loja {sem['loja']}, cargo {sem['cargo']}, turno {sem['turno']}")
    print(f"  equipe em one-hot: {pd.get_dummies(tr['equipe']).shape[1]} colunas")

    print("\n3. ordinal: um número inteiro para cada categoria")
    alfa = tr["turno"].astype("category")
    print("  turno, em ordem alfabética (cat.codes): "
          + ", ".join(f"{c} {i}" for i, c in enumerate(alfa.cat.categories)))
    print("  turno, na ordem do dia: manha 0, tarde 1, noite 2")
    taxa = tr.groupby("turno")["saiu_180d"].mean()
    print("  % saíram no treino: " + ", ".join(f"{t} {pct(taxa[t])}" for t in ["manha", "tarde", "noite"]))
    lojas = sorted(tr["loja"].unique())
    cod = pd.Categorical(novas["loja"], categories=lojas).codes
    print(f"  loja, com as categorias do treino: {lojas[0]} 0 ... {lojas[-1]} {len(lojas) - 1}; "
          f"L08 vira {int(cod[novas['loja'].to_numpy() == 'L08'][0])} em {int((cod == -1).sum())} pessoas novas")

    print("\n4. target encoding: a categoria vira a taxa de saída dela no treino")
    mapa, geral = media_por_categoria(tr, "cargo", 0)
    print("  cargo: " + ", ".join(f"{c} {pct(v)}" for c, v in mapa.items())
          + f"; cargo que o treino não tem: {pct(geral)}, a taxa de todo o treino")
    print("  equipe: acerto do par, sorteando uma pessoa que saiu e uma que ficou (50% é o de uma moeda)")
    print(f"  {'como a nota da equipe foi calculada':<44}{'no treino':>10}{'na validação':>14}")
    linhas = []
    for m, rot in [(0, ""), (SUAVIZACAO, f", suavizada com {SUAVIZACAO}")]:
        mapa, geral = media_por_categoria(tr, "equipe", m)
        nota_va = acerto_do_par(va["equipe"].map(mapa).fillna(geral), va["saiu_180d"])
        dentro = acerto_do_par(tr["equipe"].map(mapa), tr["saiu_180d"])
        oof, sem_par = fora_da_dobra(tr, "equipe", m)
        linhas.append((f"média de todo o treino{rot}", dentro, nota_va))
        linhas.append((f"fora da dobra, {DOBRAS} dobras{rot}", acerto_do_par(oof, tr["saiu_180d"]), nota_va))
    for rot, t, v in linhas:
        print(f"  {rot:<44}{pct(t):>10}{pct(v):>14}")
    junto, g2 = media_por_categoria(pd.concat([tr, va]), "equipe", 0)
    vazou = acerto_do_par(va["equipe"].map(junto).fillna(g2), va["saiu_180d"])
    print(f"  {'média de treino e validação juntos':<44}{'-':>10}{pct(vazou):>14}")
    print(f"  fora da dobra: {sem_par} pessoas do treino caem numa equipe que as outras dobras não têm "
          f"e recebem a taxa geral delas")


if __name__ == "__main__":
    main()
