"""Onde a base de admissões tem valor vazio ou extremo, e de onde ele vem.

Aula «Valores vazios e extremos» do curso ML: preparação e validação.
Rode de dentro da pasta da aula:

    python3 vazios_extremos.py

Lê ../dados/pessoas/admissoes.csv, aplica o contrato do alvo da aula 03 e a divisão por data
(treino até 2025-06-30, validação até 2025-09-30, teste até 2026-01-01). Todo número que vai
para o plano de transformação (mediana, limite de extremo, mediana do salário por cargo) é
calculado só no treino. As outras partes só recebem a regra pronta.
"""
import sys
from pathlib import Path

import pandas as pd

BASE = Path("../dados/pessoas/admissoes.csv")
FIM_CONTRATO = "2026-01-01"
FIM_TREINO = "2025-06-30"
FIM_VALIDACAO = "2025-09-30"
NA = {"validação": "na validação", "teste": "no teste"}
CAMPO_DISTANCIA = "2025-03-01"


def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(parte, todo):
    return num(100 * parte / todo) + "%" if todo else "-"


def limite_iqr(serie):
    """Limite de cima da regra de 1,5 IQR: terceiro quartil + 1,5 vezes a distância entre os quartis."""
    q1, q3 = serie.quantile([0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)


def carregar():
    if not BASE.exists():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 06-valores-vazios-e-extremos do kit.")
    a = pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])
    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    contrato = (a["data_admissao"] <= FIM_CONTRATO) & ~(dias <= 7)
    a["parte"] = "fora do contrato"
    a.loc[contrato, "parte"] = "teste"
    a.loc[contrato & (a["data_admissao"] <= FIM_VALIDACAO), "parte"] = "validação"
    a.loc[contrato & (a["data_admissao"] <= FIM_TREINO), "parte"] = "treino"
    return a


def main():
    a = carregar()
    tr = a[a["parte"] == "treino"]
    n = a["parte"].value_counts()
    print(f"admissões: {len(a)}; contrato da aula 03: {int(n.drop('fora do contrato').sum())} pessoas")
    print(f"treino: até {FIM_TREINO} ({n['treino']}); validação: até {FIM_VALIDACAO} ({n['validação']}); "
          f"teste: até {FIM_CONTRATO} ({n['teste']})")
    print("todo número do plano sai do treino")

    print("\n1. distância vazia por trimestre de admissão, nas 1500 admissões")
    print(f"  {'trimestre':<10}{'admissões':>10}{'vazia':>8}{'% vazia':>9}")
    tri = a["data_admissao"].dt.to_period("Q").astype(str).str.replace("Q", "-T")
    for t, g in a.groupby(tri):
        v = int(g["distancia_km"].isna().sum())
        print(f"  {t:<10}{len(g):>10}{v:>8}{pct(v, len(g)):>9}")

    print("\n2. no treino: quem saiu, com a distância vazia e preenchida")
    print(f"  {'grupo':<38}{'pessoas':>8}{'saíram':>8}{'% saíram':>10}")
    vazia = tr["distancia_km"].isna()
    antes = tr["data_admissao"] < CAMPO_DISTANCIA
    grupos = [("distância vazia", vazia), ("distância preenchida", ~vazia),
              (f"antes de {CAMPO_DISTANCIA}, vazia", antes & vazia),
              (f"antes de {CAMPO_DISTANCIA}, preenchida", antes & ~vazia),
              (f"desde {CAMPO_DISTANCIA}, vazia", ~antes & vazia),
              (f"desde {CAMPO_DISTANCIA}, preenchida", ~antes & ~vazia)]
    for nome, m in grupos:
        s = int(tr.loc[m, "saiu_180d"].sum())
        print(f"  {nome:<38}{int(m.sum()):>8}{s:>8}{pct(s, int(m.sum())):>10}")
    for parte in ["validação", "teste"]:
        g = a[a["parte"] == parte]
        print(f"  distância vazia {NA[parte]}: {int(g['distancia_km'].isna().sum())} de {len(g)}")

    print("\n3. o mesmo número calculado no treino e nas 1500 admissões")
    print(f"  mediana da distância: treino {num(tr['distancia_km'].median())} km; "
          f"1500 admissões {num(a['distancia_km'].median())} km")
    print(f"  limite de extremo da distância (1,5 IQR): treino {num(limite_iqr(tr['distancia_km'].dropna()), 2)} km; "
          f"1500 admissões {num(limite_iqr(a['distancia_km'].dropna()), 2)} km")

    print("\n4. extremos pela regra de 1,5 IQR, com o limite calculado no treino")
    print(f"  {'coluna':<14}{'limite':>9}{'acima no treino':>17}{'% saíram acima':>16}{'% saíram no resto':>19}")
    limites = {}
    for col in ["salario_base", "distancia_km"]:
        lim = limite_iqr(tr[col].dropna())
        limites[col] = lim
        acima = tr[col] > lim
        resto = (tr[col] <= lim)
        print(f"  {col:<14}{num(lim, 2):>9}{int(acima.sum()):>17}"
              f"{pct(int(tr.loc[acima, 'saiu_180d'].sum()), int(acima.sum())):>16}"
              f"{pct(int(tr.loc[resto, 'saiu_180d'].sum()), int(resto.sum())):>19}")
    lim = limites["salario_base"]
    for parte in ["validação", "teste"]:
        g = a[a["parte"] == parte]
        m = g["salario_base"] > lim
        cargos = ", ".join(f"{c} {k}" for c, k in g.loc[m, "cargo"].value_counts().items()) or "nenhum"
        print(f"  salário acima de {num(lim, 2)} {NA[parte]}: {int(m.sum())} de {len(g)} ({cargos})")

    print("\n5. salário fora da faixa do cargo: mais que o dobro ou menos que a metade da mediana do cargo no treino")
    med = tr.groupby("cargo")["salario_base"].median()
    geral = tr["salario_base"].median()
    for cargo, v in med.items():
        print(f"  mediana no treino, {cargo}: {v:.0f}")
    print(f"  cargo que o treino não tem: mediana geral do treino, {geral:.0f}")
    ref = a["cargo"].map(med).fillna(geral)
    fora = (a["salario_base"] > 2 * ref) | (a["salario_base"] < ref / 2)
    print(f"  {'pessoa':>6}  {'admissão':<11} {'cargo':<20}{'salário':>8}{'mediana':>9}  parte")
    for i in a.index[fora]:
        r = a.loc[i]
        print(f"  {r['id_pessoa']:>6}  {r['data_admissao'].date()!s:<11} {r['cargo']:<20}"
              f"{r['salario_base']:>8}{ref[i]:>9.0f}  {r['parte']}")


if __name__ == "__main__":
    main()
