"""Pipeline do acompanhamento no primeiro mês: ajustado no treino, aplicado pronto em qualquer pessoa.

Aula «Pipeline para dados de pessoas» do curso ML: preparação e validação.
Rode de dentro da pasta da aula:

    python3 pipeline.py           # a demonstração da aula
    python3 testar_pipeline.py    # os testes do pipeline

O pipeline junta numa peça só o contrato do alvo da aula 03, a divisão por data (treino até
2025-06-30, validação até 2025-09-30, teste até 2026-01-01), o plano de transformação da aula 06,
a escala da aula 07 e o mapa das categorias da aula 08.

- ajustar(treino) calcula todos os números com o treino e recusa linha admitida depois de 2025-06-30.
- aplicar(params, pessoas) usa só esses números. Ele não calcula nada com as linhas que recebe:
  uma pessoa sozinha sai igual a ela dentro de um lote.
- aplicar recusa linha sem data de admissão. O pipeline prepara a lista de acompanhamento de quem
  já foi contratado; ele não serve para escolher candidato.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("../dados/pessoas/admissoes.csv")
FIM_TREINO = "2025-06-30"
FIM_VALIDACAO = "2025-09-30"
FIM_CONTRATO = "2026-01-01"
NUMERICAS = ["salario_base", "distancia_km", "indicacao"]
CATEGORIAS = ["loja", "cargo", "turno"]
DISTANCIA_MAX = 100
NOME = {"loja": "loja", "cargo": "cargo", "turno": "turno"}


# ---------------------------------------------------------------- leitura e divisão

def carregar(base=BASE):
    if not Path(base).exists():
        sys.exit(f"não achei {base}. Rode de dentro da pasta 09-pipeline-para-dados-de-pessoas do kit.")
    return pd.read_csv(base, parse_dates=["data_admissao", "data_desligamento"])


def separar(a):
    """Treino, validação e pessoas novas. O teste sai aqui e não volta."""
    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    contrato = (a["data_admissao"] <= FIM_CONTRATO) & ~(dias <= 7)
    treino = a[contrato & (a["data_admissao"] <= FIM_TREINO)]
    validacao = a[contrato & (a["data_admissao"] > FIM_TREINO) & (a["data_admissao"] <= FIM_VALIDACAO)]
    teste = a[contrato & (a["data_admissao"] > FIM_VALIDACAO)]
    novas = a[a["data_admissao"] > FIM_CONTRATO]
    return treino, validacao, len(teste), novas


# ---------------------------------------------------------------- o pipeline

def _corrigir(params, p):
    """Plano da aula 06 com os números do treino. Retorna as colunas corrigidas e os avisos."""
    p = p.copy()
    for c in NUMERICAS:
        p[c] = pd.to_numeric(p[c])  # texto numa coluna de número para com erro
    avisos =pd.Series([[] for _ in range(len(p))], index=p.index)
    sem_nota = pd.Series(False, index=p.index)

    def avisar(mascara, texto, bloqueia=False):
        for i in p.index[mascara]:
            avisos[i] = avisos[i] + [texto]
        if bloqueia:
            sem_nota[mascara] = True

    d = p["distancia_km"]
    fora = (d < 0) | (d > DISTANCIA_MAX)
    avisar(fora, "distância fora da faixa")
    p["distancia_km"] = d.mask(fora).fillna(params["mediana_distancia"])

    for c in CATEGORIAS:
        vazio = p[c].isna()
        avisar(vazio, f"{NOME[c]} vazio", bloqueia=True)
        avisar(~vazio & ~p[c].isin(params["categorias"][c]), f"{NOME[c]} que o treino não tem")
    ind = p["indicacao"]
    avisar(ind.isna() | ~ind.isin([0, 1]), "indicação vazia ou fora de 0 e 1", bloqueia=True)

    s = p["salario_base"]
    ref = p["cargo"].map(params["mediana_salario_cargo"]).fillna(params["mediana_salario_geral"])
    avisar(s.isna(), "salário vazio", bloqueia=True)
    fora = (s > 2 * ref) | (s < ref / 2)
    avisar(fora, "salário fora da faixa do cargo")
    p["salario_base"] = s.mask(fora, ref)
    return p, avisos, sem_nota


def ajustar(treino):
    """Calcula todos os números do pipeline com o treino. Recusa qualquer linha de depois do treino."""
    if len(treino) == 0:
        raise ValueError("ajustar recebeu uma base vazia")
    depois = int((treino["data_admissao"] > FIM_TREINO).sum())
    if depois:
        raise ValueError(f"ajustar só recebe o treino: {depois} pessoas admitidas depois de {FIM_TREINO}")
    d = treino["distancia_km"]
    params = {
        "treino_ate": FIM_TREINO,
        "pessoas_no_treino": int(len(treino)),
        "mediana_distancia": float(d[(d >= 0) & (d <= DISTANCIA_MAX)].median()),
        "mediana_salario_cargo": {k: float(v) for k, v in treino.groupby("cargo")["salario_base"].median().items()},
        "mediana_salario_geral": float(treino["salario_base"].median()),
        "categorias": {c: sorted(treino[c].dropna().unique().tolist()) for c in CATEGORIAS},
    }
    corrigido, _, _ = _corrigir(params, treino)
    params["media"] = {c: float(corrigido[c].mean()) for c in NUMERICAS}
    params["desvio"] = {c: float(corrigido[c].std(ddof=0)) for c in NUMERICAS}  # como o StandardScaler
    params["colunas"] = NUMERICAS + [f"{c}_{v}" for c in CATEGORIAS for v in params["categorias"][c]]
    return params


def aplicar(params, pessoas):
    """A tabela que o modelo recebe, sempre com as mesmas colunas, mais `liberada` e `aviso`."""
    if "data_admissao" not in pessoas or pessoas["data_admissao"].isna().any():
        raise ValueError("aplicar só recebe pessoas já contratadas, com data de admissão. "
                         "A lista é de acompanhamento no primeiro mês, não de escolha de candidato.")
    p, avisos, sem_nota = _corrigir(params, pessoas[["id_pessoa"] + NUMERICAS + CATEGORIAS])
    x = pd.DataFrame(index=p.index)
    for c in NUMERICAS:
        x[c] = (p[c] - params["media"][c]) / params["desvio"][c]
    for c in CATEGORIAS:
        for v in params["categorias"][c]:
            x[f"{c}_{v}"] = (p[c] == v).astype(int)
    x = x[params["colunas"]].astype(float)
    x.loc[sem_nota, :] = np.nan
    x["liberada"] = ~sem_nota
    x["aviso"] = avisos.map("; ".join)
    x.index = p["id_pessoa"].to_numpy()
    x.index.name = "id_pessoa"
    return x


def resumo(saida):
    """Quantas pessoas recebem cada aviso."""
    return saida["aviso"].str.split("; ").explode().loc[lambda s: s != ""].value_counts()


# ---------------------------------------------------------------- a versão do Rafael, para comparar

def preparar_recalculando(base):
    """A preparação do Rafael: cada número sai das linhas que a função recebe."""
    p = base.copy()
    p["distancia_km"] = p["distancia_km"].fillna(p["distancia_km"].median())
    for c in ["salario_base", "distancia_km", "indicacao"]:
        p[c] = (p[c] - p[c].mean()) / p[c].std(ddof=0)
    return pd.concat([p[NUMERICAS], pd.get_dummies(p[CATEGORIAS])], axis=1)


# ---------------------------------------------------------------- demonstração

def num(x, casas=2):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(parte, todo):
    return num(100 * parte / todo, 1) + "%"


def main():
    a = carregar()
    treino, validacao, n_teste, novas = separar(a)
    print(f"contrato da aula 03: {len(treino) + len(validacao) + n_teste} pessoas; treino até {FIM_TREINO} "
          f"({len(treino)}); validação até {FIM_VALIDACAO} ({len(validacao)}); teste: {n_teste}, fechado")
    print(f"pessoas novas, admitidas depois de {FIM_CONTRATO}: {len(novas)}")

    print("\n1. ajustar: o que o pipeline guarda, tudo calculado no treino")
    params = ajustar(treino)
    print(f"  distância vazia vira {num(params['mediana_distancia'], 1)} km, a mediana do treino")
    print("  salário fora da faixa vira a mediana do cargo: "
          + ", ".join(f"{k} {v:.0f}" for k, v in params["mediana_salario_cargo"].items())
          + f"; cargo que o treino não tem {params['mediana_salario_geral']:.0f}")
    for c in NUMERICAS:
        print(f"  escala de {c}: tira {num(params['media'][c])} e divide por {num(params['desvio'][c])}")
    for c in CATEGORIAS:
        print(f"  colunas de {c}: {len(params['categorias'][c])} ({', '.join(params['categorias'][c])})")
    print(f"  colunas que saem: {len(params['colunas'])}, sempre na mesma ordem")

    print("\n2. a preparação do Rafael: cada número sai das linhas que ela recebe")
    um = novas.head(1)
    print(f"  {'base que ela recebe':<26}{'mediana distância':>18}{'divide o salário por':>22}{'colunas':>9}")
    for nome, b in [("o treino", treino), ("as 1500 admissões", a), ("a validação sozinha", validacao),
                    ("uma pessoa nova", um)]:
        med = b["distancia_km"].median()
        dsv = b["salario_base"].std(ddof=0)
        cols = preparar_recalculando(b).shape[1]
        print(f"  {nome:<26}{(num(med, 1) + ' km') if pd.notna(med) else 'vazia':>18}{num(dsv):>22}{cols:>9}")
    r = preparar_recalculando(um)
    print(f"  na pessoa nova {int(um['id_pessoa'].iloc[0])}: salário {r['salario_base'].iloc[0]}, "
          f"distância {r['distancia_km'].iloc[0]}, indicação {r['indicacao'].iloc[0]}")

    print("\n3. aplicar: validação e pessoas novas com os números do treino")
    for nome, b in [("validação", validacao), ("pessoas novas", novas)]:
        s = aplicar(params, b)
        avisos = resumo(s)
        txt = ", ".join(f"{k} {v}" for k, v in avisos.items()) or "nenhum"
        print(f"  {nome}: {len(s)} pessoas, {len(params['colunas'])} colunas, {int(s['liberada'].sum())} liberadas; "
              f"avisos: {txt}")
    s_novas = aplicar(params, novas)
    nova_cat = s_novas["aviso"].str.contains("loja que o treino não tem|cargo que o treino não tem")
    print(f"  pessoas novas com loja ou cargo que o treino não tem: {int(nova_cat.sum())} de {len(novas)} "
          f"({pct(int(nova_cat.sum()), len(novas))}); passa de 1 em cada 10: o mapa da aula 08 volta para a mesa")
    print(f"  média da escala na validação: salário {num(aplicar(params, validacao)['salario_base'].mean())}, "
          f"distância {num(aplicar(params, validacao)['distancia_km'].mean())} (não é 0: a escala é do treino)")

    print("\n4. uma pessoa por vez dá o mesmo que o lote")
    lote = aplicar(params, novas)
    um_a_um = pd.concat([aplicar(params, novas.iloc[[i]]) for i in range(len(novas))])
    num_cols = params["colunas"]
    dif = float(np.nanmax(np.abs(lote[num_cols].to_numpy() - um_a_um[num_cols].to_numpy())))
    iguais = lote[["liberada", "aviso"]].equals(um_a_um[["liberada", "aviso"]])
    print(f"  {len(novas)} pessoas novas aplicadas uma a uma: maior diferença {num(dif, 1)}; avisos iguais: "
          f"{'sim' if iguais else 'não'}; colunas iguais: {'sim' if list(um_a_um.columns) == list(lote.columns) else 'não'}")

    print("\n5. o que o pipeline recusa")
    for nome, func in [("ajustar com treino e validação juntos", lambda: ajustar(pd.concat([treino, validacao]))),
                       ("aplicar numa linha sem data de admissão",
                        lambda: aplicar(params, novas.head(1).assign(data_admissao=pd.NaT)))]:
        try:
            func()
            print(f"  {nome}: passou")
        except ValueError as erro:
            print(f"  {nome}: ValueError: {erro}")


if __name__ == "__main__":
    main()
