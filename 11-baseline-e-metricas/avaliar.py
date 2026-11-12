"""A tabela de avaliação da aula «Baseline e métricas» do curso ML: preparação e validação.

    python3 avaliar.py                      # a tabela da aula, com os preços do briefing da aula 01
    python3 avaliar.py --cancelamento 30    # outro preço para o cancelamento que passa
    python3 avaliar.py --varrer             # o custo do classificador em vários cortes

Todas as regras são medidas nos mesmos 795 pedidos da validação (abril e maio de 2026).
O classificador é o da aula 10: a preparação corrigida (pipeline_corrigido.py) e a regressão
logística pronta (classificador.py), ajustadas nos pedidos de janeiro a março.
Junho, o teste, sai na leitura e não entra em nenhuma conta.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("../dados/loja/pedidos_export_completo.csv")
LIGACAO = 5          # R$ de uma ligação, acerte ou não (briefing da aula 01)
CANCELAMENTO = 15    # R$ de um cancelamento que passa sem ligação
TETO = 0.25          # no máximo 1 ligação para cada 4 pedidos


def carregar():
    if not BASE.is_file() or not Path("classificador.py").is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 11-baseline-e-metricas do kit.")
    import classificador
    import pipeline_corrigido
    base = pd.read_csv(BASE, parse_dates=["data_pedido"])
    x_tr, y_tr, x_va, y_va = pipeline_corrigido.preparar(base)
    modelo = classificador.treinar(x_tr, y_tr)
    nota = classificador.nota(modelo, x_va)
    validacao = base.set_index("id_pedido").loc[y_va.index]
    return validacao, y_va, nota, len(y_tr)


def matriz(y, ligar):
    """VP, FP, FN, VN de uma regra. y e ligar com o mesmo tamanho, 0/1."""
    y = np.asarray(y).astype(int)
    ligar = np.asarray(ligar).astype(bool)
    if len(y) != len(ligar):
        raise ValueError(f"y tem {len(y)} linhas e a regra tem {len(ligar)}")
    return {"vp": int((ligar & (y == 1)).sum()), "fp": int((ligar & (y == 0)).sum()),
            "fn": int((~ligar & (y == 1)).sum()), "vn": int((~ligar & (y == 0)).sum())}


def linha(y, ligar, ligacao=LIGACAO, cancelamento=CANCELAMENTO):
    m = matriz(y, ligar)
    n = sum(m.values())
    ligacoes = m["vp"] + m["fp"]
    return {**m, "ligacoes": ligacoes, "parte": ligacoes / n,
            "precisao": m["vp"] / ligacoes if ligacoes else None,   # ninguém marcado: não existe
            "revocacao": m["vp"] / (m["vp"] + m["fn"]) if m["vp"] + m["fn"] else None,
            "acuracia": (m["vp"] + m["vn"]) / n,
            "custo": ligacao * ligacoes + cancelamento * m["fn"]}


def regras(validacao, nota, empate):
    return {
        "nunca liga": np.zeros(len(nota), dtype=bool),
        "liga para todos": np.ones(len(nota), dtype=bool),
        "boleto": (validacao["forma_pagamento"] == "boleto").to_numpy(),
        "classificador, corte 0,5": (nota > 0.5).to_numpy(),
        f"classificador, corte {num(empate, 3)}": (nota > empate).to_numpy(),
    }


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ligacao", type=float, default=LIGACAO, help="R$ de uma ligação")
    ap.add_argument("--cancelamento", type=float, default=CANCELAMENTO, help="R$ de um cancelamento que passa")
    ap.add_argument("--varrer", action="store_true", help="custo do classificador em vários cortes")
    args = ap.parse_args()
    lig, canc = args.ligacao, args.cancelamento
    empate = lig / canc

    validacao, y, nota, n_treino = carregar()
    n = len(y)
    print(f"validação: {n} pedidos de abril e maio de 2026, {int(y.sum())} cancelados ({pct(y.mean())}); "
          "junho, o teste, fica fora")
    print(f"classificador: o da aula 10, ajustado nos {n_treino} pedidos de janeiro a março")
    print(f"preços: ligação R$ {num(lig, 0)}, cancelamento sem ligação R$ {num(canc, 0)}; "
          f"empate {pct(empate)}; teto: 1 ligação para cada 4 pedidos ({int(n * TETO)} aqui)")

    if args.varrer:
        print("\no classificador em vários cortes (liga quando a nota passa do corte)")
        print(f"{'corte':>6} {'ligações':>9} {'precisão':>9} {'revocação':>10} {'custo':>9} {'cabe?':>6}")
        for corte in sorted({0.20, 0.25, 0.30, empate, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60}):
            r = linha(y, nota > corte, lig, canc)
            marca = "  <- o empate" if corte == empate else ""
            print(f"{num(corte, 3):>6} {r['ligacoes']:>9} {pct(r['precisao']):>9} {pct(r['revocacao']):>10} "
                  f"{reais(r['custo']):>9} {'sim' if r['parte'] <= TETO else 'não':>6}{marca}")
        return

    tabela = {nome: linha(y, ligar, lig, canc) for nome, ligar in regras(validacao, nota, empate).items()}

    print("\n1. a matriz de cada regra")
    print("   VP: ligou e ia cancelar; FP: ligou à toa; FN: cancelou sem ligação; VN: nada acontece")
    print(f"{'regra':<30} {'VP':>4} {'FP':>4} {'FN':>4} {'VN':>4} {'acurácia':>9}")
    for nome, r in tabela.items():
        print(f"{nome:<30} {r['vp']:>4} {r['fp']:>4} {r['fn']:>4} {r['vn']:>4} {pct(r['acuracia']):>9}")

    print("\n2. a tabela de avaliação")
    print(f"{'regra':<30} {'ligações':>8} {'% pedidos':>9} {'precisão':>9} {'revocação':>10} {'custo':>9} "
          f"{'economia':>9} {'cabe?':>6}")
    base_custo = tabela["nunca liga"]["custo"]
    for nome, r in tabela.items():
        print(f"{nome:<30} {r['ligacoes']:>8} {pct(r['parte']):>9} {pct(r['precisao']):>9} "
              f"{pct(r['revocacao']):>10} {reais(r['custo']):>9} {reais(base_custo - r['custo']):>9} "
              f"{'sim' if r['parte'] <= TETO else 'não':>6}")
    print("   custo: ligações × preço da ligação + cancelamentos sem ligação × preço do cancelamento")
    print("   economia: contra não ligar para ninguém, nos mesmos pedidos")

    print("\n3. o classificador contra a regra a vencer, o boleto")
    b = tabela["boleto"]
    for nome in [k for k in tabela if k.startswith("classificador")]:
        r = tabela[nome]
        dif = r["custo"] - b["custo"]
        print(f"{nome}: {r['ligacoes'] - b['ligacoes']:+d} ligações, {r['vp'] - b['vp']:+d} certas; "
              f"custa {reais(abs(dif))} {'a menos' if dif < 0 else 'a mais'} que o boleto")
    acima = (nota > empate).to_numpy()
    print(f"pedidos com nota acima de {num(empate, 3)}: nota média {pct(float(nota[acima].mean()))}, "
          f"cancelaram {pct(float(y[acima].mean()))}")

    import classificador
    boleto = (validacao["forma_pagamento"] == "boleto").astype(int).to_numpy()
    print("\n4. o acerto do par da aula 08, que não depende do corte")
    print(f"classificador: {pct(classificador.acerto_do_par(nota, y))}; "
          f"boleto como nota 0 ou 1: {pct(classificador.acerto_do_par(boleto, y))}; "
          f"nunca liga, a mesma nota para todos: {pct(classificador.acerto_do_par(np.zeros(n), y))}")


if __name__ == "__main__":
    main()
