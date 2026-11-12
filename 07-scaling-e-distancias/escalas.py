"""O que MinMax, Standard e Robust fazem com uma distância entre pessoas.

Aula «Scaling e distâncias» do curso ML: preparação e validação.
Rode de dentro da pasta da aula:

    python3 escalas.py

Lê ../dados/pessoas/admissoes.csv, aplica o contrato do alvo da aula 03, a divisão por data
(treino até 2025-06-30, validação até 2025-09-30, teste até 2026-01-01) e o plano de
transformação da aula 06 (distância vazia vira a mediana do treino; salário fora da faixa do
cargo vira a mediana do cargo no treino). Depois calcula as três escalas no treino e mostra o
que cada uma faz com o modelo de vizinhos: para cada pessoa, ele procura as 25 pessoas do
treino mais perto dela e usa a taxa de saída delas como nota.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("../dados/pessoas/admissoes.csv")
FIM_CONTRATO = "2026-01-01"
FIM_TREINO = "2025-06-30"
FIM_VALIDACAO = "2025-09-30"
COLUNAS = ["salario_base", "distancia_km", "indicacao"]
NOMES = {"salario_base": "salário", "distancia_km": "distância", "indicacao": "indicação"}
VIZINHOS = 25
LISTA = 36  # 12 pessoas por mês, nos três meses da validação
CORTE_ARVORE = 21.5  # o limite de extremo da distância na aula 06
ESCALAS = ["sem escala", "MinMax", "Standard", "Robust"]


def num(x, casas=2):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return num(100 * x, 1) + "%"


def carregar():
    if not BASE.exists():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 07-scaling-e-distancias do kit.")
    a = pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])
    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    a = a[(a["data_admissao"] <= FIM_CONTRATO) & ~(dias <= 7)].sort_values("id_pessoa").copy()
    a["parte"] = "teste"
    a.loc[a["data_admissao"] <= FIM_VALIDACAO, "parte"] = "validação"
    a.loc[a["data_admissao"] <= FIM_TREINO, "parte"] = "treino"
    return a


def plano_da_aula_06(a, corrigir_salario=True):
    """Os números saem do treino e são aplicados prontos nas três partes."""
    tr = a[a["parte"] == "treino"]
    a = a.copy()
    a["distancia_km"] = a["distancia_km"].fillna(tr["distancia_km"].median())
    if corrigir_salario:
        med = tr.groupby("cargo")["salario_base"].median()
        ref = a["cargo"].map(med).fillna(tr["salario_base"].median())
        fora = (a["salario_base"] > 2 * ref) | (a["salario_base"] < ref / 2)
        a.loc[fora, "salario_base"] = ref[fora]
    return a


def escala(X, nome):
    """Quanto tirar e por quanto dividir em cada coluna, calculados só com as linhas de X (o treino)."""
    if nome == "sem escala":
        return np.zeros(X.shape[1]), np.ones(X.shape[1])
    if nome == "MinMax":
        return X.min(axis=0), X.max(axis=0) - X.min(axis=0)
    if nome == "Standard":
        return X.mean(axis=0), X.std(axis=0)  # desvio padrão com ddof=0, como o StandardScaler
    q1, q3 = np.percentile(X, [25, 75], axis=0)
    return np.median(X, axis=0), q3 - q1


def vizinhos(Z_treino, z):
    """Posições das 25 pessoas do treino mais perto de z, pela distância de sempre (euclidiana)."""
    d = np.sqrt(((Z_treino - z) ** 2).sum(axis=1))
    return np.argsort(d, kind="stable")[:VIZINHOS]


def main():
    a = plano_da_aula_06(carregar())
    tr, va, te = (a[a["parte"] == p] for p in ["treino", "validação", "teste"])
    X, y = tr[COLUNAS].to_numpy(float), tr["saiu_180d"].to_numpy()
    Xv, yv = va[COLUNAS].to_numpy(float), va["saiu_180d"].to_numpy()
    print(f"contrato da aula 03: {len(a)} pessoas; treino {len(tr)}, validação {len(va)}, teste {len(te)}")
    print("antes da escala, o plano da aula 06: distância vazia vira 5,2 km; "
          "salário fora da faixa do cargo vira a mediana do cargo")
    print("colunas do modelo de vizinhos: " + ", ".join(COLUNAS) + "; toda escala sai do treino")

    print("\n1. o que cada escala calcula no treino")
    print(f"  {'escala':<10}{'coluna':<14}{'tira':>10}{'divide por':>12}")
    params = {n: escala(X, n) for n in ESCALAS}
    for n in ESCALAS[1:]:
        c, s = params[n]
        for j, col in enumerate(COLUNAS):
            print(f"  {n:<10}{col:<14}{num(c[j]):>10}{num(s[j]):>12}")

    print("\n2. o salário sem a correção da aula 06 (pessoas 440 e 396, com um zero a mais)")
    bruto = plano_da_aula_06(carregar(), corrigir_salario=False)
    Xb = bruto[bruto["parte"] == "treino"][COLUNAS].to_numpy(float)
    print(f"  {'escala':<10}{'divide por':>12}{'R$ 2.400 vira':>15}{'sem corrigir':>14}{'R$ 2.400 vira':>15}")
    for n in ESCALAS[1:]:
        (c, s), (cb, sb) = params[n], escala(Xb, n)
        print(f"  {n:<10}{num(s[0]):>12}{num((2400 - c[0]) / s[0]):>15}"
              f"{num(sb[0]):>14}{num((2400 - cb[0]) / sb[0]):>15}")

    print("\n3. quanto cada coluna pesa na distância entre duas pessoas do treino, em média")
    print(f"  {'escala':<12}" + "".join(f"{NOMES[c]:>11}" for c in COLUNAS))
    for n in ESCALAS:
        c, s = params[n]
        v = ((X - c) / s).var(axis=0)
        print(f"  {n:<12}" + "".join(f"{pct(x):>11}" for x in v / v.sum()))
    q1, q3 = np.percentile(X[:, 1], [25, 75])
    print(f"  distância no treino, depois de preencher: metade do meio de {num(q1)} a {num(q3)} km; "
          f"{int((X[:, 1] == 5.2).sum())} de {len(tr)} pessoas com 5,2 km")

    i = int(np.argmax(Xv[:, 1]))
    p = va.iloc[i]
    print(f"\n4. os {VIZINHOS} vizinhos da pessoa {p['id_pessoa']}, da validação: "
          f"{num(Xv[i, 1], 1)} km, indicação {int(Xv[i, 2])}, salário {Xv[i, 0]:.0f}")
    print(f"  {'escala':<12}{'distância média':>16}{'salário médio':>15}{'com indicação':>15}{'saíram':>8}")
    for n in ESCALAS:
        c, s = params[n]
        perto = vizinhos((X - c) / s, (Xv[i] - c) / s)
        print(f"  {n:<12}{num(X[perto, 1].mean(), 1) + ' km':>16}{X[perto, 0].mean():>15.0f}"
              f"{int(X[perto, 2].sum()):>15}{int(y[perto].sum()):>8}")

    print(f"\n5. a árvore só pergunta se passa de um corte: pessoas do treino acima de {num(CORTE_ARVORE)} km")
    for n in ESCALAS:
        c, s = params[n]
        corte = (CORTE_ARVORE - c[1]) / s[1]
        acima = ((X[:, 1] - c[1]) / s[1]) > corte
        print(f"  {n:<12}corte {num(corte):>6}: {int(acima.sum())} pessoas, {int(y[acima].sum())} saíram")

    print("\n6. o teste com o MinMax do treino: quem passa de 1")
    c, s = params["MinMax"]
    Zt = (te[COLUNAS].to_numpy(float) - c) / s
    for j, col in enumerate(COLUNAS):
        fora = Zt[:, j] > 1
        cargos = ", ".join(f"{k} {v}" for k, v in te.loc[fora, "cargo"].value_counts().items()) or "nenhum"
        print(f"  {col:<14}maior {num(Zt[:, j].max()):>5}; acima de 1: {int(fora.sum())} de {len(te)} ({cargos})")

    print(f"\n7. na validação: quantas das {LISTA} maiores notas saíram (12 por mês, três meses)")
    for n in ESCALAS:
        c, s = params[n]
        Z = (X - c) / s
        r = np.array([y[vizinhos(Z, z)].mean() for z in (Xv - c) / s])
        lista = np.argsort(-r, kind="stable")[:LISTA]
        print(f"  {n:<12}{int(yv[lista].sum()):>2} de {LISTA}; distância média da lista "
              f"{num(Xv[lista, 1].mean(), 1)} km")
    print(f"  {len(yv)} pessoas na validação, {int(yv.sum())} saíram; uma lista sorteada acharia "
          f"{num(LISTA * yv.mean(), 1)} em média")


if __name__ == "__main__":
    main()
