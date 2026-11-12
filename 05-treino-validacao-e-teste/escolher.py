"""Ajusta as tabelas de risco no treino e escolhe uma pela validação. O teste fica de fora.

    python3 escolher.py

Cada candidata é uma tabela: a taxa de cancelamento do treino em cada combinação de colunas.
Ela liga para o pedido quando a taxa da combinação dele passa do ponto de empate da aula 01
(R$ 5 / R$ 15 = 1 em cada 3). A regra de escolha está escrita em REGRA_DA_ESCOLHA, antes de rodar.
"""
import sys

import pandas as pd

from particoes import ARQUIVO, BASE, checar

LIGACAO, CANCELAMENTO = 5, 15
EMPATE = LIGACAO / CANCELAMENTO
TETO_LIGACOES = 0.25            # no máximo 1 ligação para cada 4 pedidos
FOLGA = 5.0                     # R$ por 100 pedidos: uma ligação à toa a cada 100 pedidos
REGRA_DA_ESCOLHA = ("maior economia por 100 pedidos na validação, entre as que ligam para no máximo 1 de "
                    "cada 4 pedidos; se a segunda ficar a menos de R$ 5 da primeira, fica a de menos células")
CANDIDATAS = [
    ("boleto (regra da aula 01)", None),
    ("pagamento + cliente", ["forma_pagamento", "cliente"]),
    ("pagamento + cliente + categoria", ["forma_pagamento", "cliente", "categoria"]),
    ("pagamento + cliente + categoria + prazo", ["forma_pagamento", "cliente", "categoria", "prazo"]),
    ("as cinco colunas", ["forma_pagamento", "cliente", "categoria", "prazo", "valor_faixa"]),
]


def preparar(pedidos):
    p = pedidos.copy()
    p["cliente"] = p["cliente_novo"].map({1: "novo", 0: "antigo"})
    p["prazo"] = pd.cut(p["prazo_prometido_dias"], [0, 5, 10, 99], labels=["até 5", "6 a 10", "11 ou mais"]).astype(str)
    p["valor_faixa"] = pd.cut(p["valor"], [0, 100, 500, float("inf")],
                              labels=["até 100", "100 a 500", "acima de 500"]).astype(str)
    return p


def ajustar(treino, colunas):
    """A tabela é só a taxa de cancelamento de cada combinação, contada no treino."""
    if colunas is None:
        return None
    return treino.groupby(colunas)["cancelado"].mean()


def ligar(tabela, colunas, d):
    if colunas is None:
        return d["forma_pagamento"] == "boleto"
    chaves = pd.MultiIndex.from_frame(d[colunas])
    taxa = pd.Series(tabela.reindex(chaves).to_numpy(), index=d.index)
    return taxa.fillna(0) > EMPATE          # combinação que o treino não viu: não liga


def medir(liga, d):
    certas = int((liga & (d["cancelado"] == 1)).sum())
    n_lig = int(liga.sum())
    return {"ligações": n_lig / len(d), "precisão": certas / n_lig if n_lig else None,
            "revocação": certas / int(d["cancelado"].sum()),
            "economia": (CANCELAMENTO * certas - LIGACAO * n_lig) / len(d) * 100}


def pct(x):
    return "-" if x is None else f"{x * 100:.1f}%".replace(".", ",")


def reais(x):
    return f"R$ {x:.2f}".replace(".", ",").replace("R$ -", "-R$ ")


def main():
    if not checar(ARQUIVO, mostrar=False):
        sys.exit(f"{ARQUIVO} não bate com a regra ou com o manifesto. Rode python3 particoes.py --checar {ARQUIVO}.")
    tudo = pd.read_csv(BASE).merge(pd.read_csv(ARQUIVO), on="id_pedido")
    n_teste = int((tudo["parte"] == "teste").sum())
    tudo = preparar(tudo[tudo["parte"] != "teste"])     # o teste sai aqui, antes de qualquer conta
    treino, validacao = tudo[tudo["parte"] == "treino"], tudo[tudo["parte"] == "validação"]
    print(f"treino: {len(treino)} pedidos; validação: {len(validacao)}; teste: {n_teste}, fora dessa conta")
    print(f"liga quando a taxa da combinação no treino passa de {pct(EMPATE)}; economia contra não ligar, "
          "por 100 pedidos\n")

    resultados = []
    for nome, colunas in CANDIDATAS:
        tabela = ajustar(treino, colunas)
        celulas = "-" if tabela is None else str(len(tabela))
        r_tr = medir(ligar(tabela, colunas, treino), treino)
        r_va = medir(ligar(tabela, colunas, validacao), validacao)
        resultados.append((nome, celulas, r_tr, r_va))

    for parte, i in [("no treino", 2), ("na validação", 3)]:
        print(f"{parte:<40} {'células':>7} {'ligações':>8} {'precisão':>8} {'revocação':>9} {'economia':>9}")
        for r in resultados:
            m = r[i]
            print(f"{r[0]:<40} {r[1]:>7} {pct(m['ligações']):>8} {pct(m['precisão']):>8} {pct(m['revocação']):>9} "
                  f"{reais(m['economia']):>9}")
        print()

    cabem = [r for r in resultados if r[3]["ligações"] <= TETO_LIGACOES]
    ordem = sorted(cabem, key=lambda r: -r[3]["economia"])
    escolhida = ordem[0]
    perto = [r for r in ordem[1:] if escolhida[3]["economia"] - r[3]["economia"] < FOLGA]
    print(f"regra da escolha: {REGRA_DA_ESCOLHA}")
    print(f"maior economia na validação: {escolhida[0]}, {reais(escolhida[3]['economia'])}")
    if perto:
        vizinhas = ", ".join(f"{r[0]} ({reais(r[3]['economia'])})" for r in perto)
        print(f"a menos de R$ 5 dela: {vizinhas}")
        escolhida = min([escolhida] + perto, key=lambda r: 0 if r[1] == "-" else int(r[1]))
    print(f"escolhida: {escolhida[0]}, {escolhida[1]} células")
    print(f"número da escolha, na validação: {reais(escolhida[3]['economia'])} por 100 pedidos "
          "(serviu para escolher; não é a medida para a gerente)")
    print("o teste continua fechado")


if __name__ == "__main__":
    main()
