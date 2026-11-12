"""Pesos, subamostragem, sobreamostragem e SMOTE: aula «Desbalanceamento e prevalência».

Curso ML: preparação e validação.

    python3 reamostragem.py                     # os cinco blocos da aula
    python3 reamostragem.py --proporcao 0.33    # leva o treino para 33% de cancelados, não 50%
    python3 reamostragem.py --prevalencia 0.30  # acrescenta o bloco 6: a validação num mês com 30%

Treino: pedidos de janeiro a março de 2026. Validação: abril e maio. Junho, o teste, sai na
leitura (pipeline_corrigido.preparar) e não entra em nenhuma conta.
A preparação e o classificador são os da aula 10. Toda estratégia mexe só no treino.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("../dados/loja/pedidos_export_completo.csv")
LIGACAO = 5            # R$ de uma ligação (briefing da aula 01)
CANCELAMENTO = 15      # R$ de um cancelamento que passa sem ligação
EMPATE = LIGACAO / CANCELAMENTO
TETO = 0.25            # no máximo 1 ligação para cada 4 pedidos
REGUA = 0.40           # precisão e revocação mínimas da régua da aula 01
VIZINHOS = 5           # o SMOTE e o modelo de vizinhos do bloco 4 olham 5 vizinhos
SORTEIO = 13           # sorteio fixo: a saída é a mesma toda vez
ESTRATEGIAS = ["nada", "peso", "subamostragem", "sobreamostragem", "SMOTE"]


# ---------------------------------------------------------------- as quatro estratégias

def treinar_com_peso(x, y, peso):
    """A mesma regressão logística do classificador.py, com um peso por linha.

    Peso 1 em todas as linhas dá exatamente o classificador.treinar.
    """
    import classificador
    m = np.c_[np.ones(len(x)), np.asarray(x, dtype=float)]
    y = np.asarray(y, dtype=float)
    w = np.asarray(peso, dtype=float)
    pesos = np.zeros(m.shape[1])
    pen = np.eye(m.shape[1]) * classificador.PENALIDADE
    pen[0, 0] = 0
    with np.errstate(all="ignore"):
        for _ in range(classificador.PASSOS):
            p = 1 / (1 + np.exp(-(m @ pesos)))
            grad = m.T @ (w * (p - y)) + pen @ pesos
            hess = m.T @ (m * (w * p * (1 - p))[:, None]) + pen
            pesos = pesos - np.linalg.solve(hess, grad)
    return {"colunas": list(x.columns), "pesos": pesos}


def vizinhos_de(a, b, k):
    """Para cada linha de a, as k linhas de b mais perto (distância euclidiana)."""
    d = ((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)
    return np.argsort(d, axis=1, kind="stable")[:, :k]


def smote(x_pos, n, k, rng):
    """n cancelados novos, cada um num ponto da reta entre um cancelado e um dos k vizinhos dele.

    Retorna as linhas novas e, para cada uma, os dois cancelados de onde ela saiu.
    """
    viz = vizinhos_de(x_pos, x_pos, k + 1)[:, 1:]          # o primeiro vizinho é ele mesmo
    a = rng.integers(0, len(x_pos), n)
    b = viz[a, rng.integers(0, k, n)]
    t = rng.random(n)[:, None]
    return x_pos[a] + t * (x_pos[b] - x_pos[a]), np.c_[a, b]


def rebalancear(x, y, estrategia, proporcao, rng):
    """Aplica a estratégia ao treino recebido. Retorna x, y, peso e a origem de cada linha.

    origem[i] = (pai1, pai2): a linha do treino recebido de onde a linha i saiu. Linha original e
    cópia têm pai1 = pai2 = ela mesma; linha do SMOTE tem os dois cancelados que a geraram.
    """
    y = np.asarray(y).astype(int)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    n1, n0 = len(pos), len(neg)
    original = np.c_[np.arange(len(y)), np.arange(len(y))]
    um = np.ones(len(y))
    if estrategia == "nada":
        return x, y, um, original
    if estrategia == "peso":
        return x, y, np.where(y == 1, proporcao / (1 - proporcao) * n0 / n1, 1.0), original
    if estrategia == "subamostragem":
        fica = int(round(n1 * (1 - proporcao) / proporcao))
        sel = np.sort(np.r_[pos, rng.choice(neg, fica, replace=False)])
        return x.iloc[sel], y[sel], np.ones(len(sel)), original[sel]
    novos = int(round(n0 * proporcao / (1 - proporcao))) - n1
    if estrategia == "sobreamostragem":
        sel = np.r_[np.arange(len(y)), rng.choice(pos, novos, replace=True)]
        return x.iloc[sel], y[sel], np.ones(len(sel)), original[sel]
    if estrategia == "SMOTE":
        linhas, pais = smote(x.to_numpy(float)[pos], novos, VIZINHOS, rng)
        xn = pd.concat([x, pd.DataFrame(linhas, columns=x.columns)], ignore_index=True)
        return xn, np.r_[y, np.ones(novos, int)], np.ones(len(xn)), np.r_[original, pos[pais]]
    raise ValueError(f"estratégia desconhecida: {estrategia}")


def fator_da_escala(y, proporcao):
    """Quantas vezes a estratégia multiplicou a chance (cancela ÷ não cancela) do treino."""
    y = np.asarray(y)
    return (proporcao / (1 - proporcao)) / (y.mean() / (1 - y.mean()))


def corrigir(nota, fator):
    """Volta a nota para a proporção do treino original: divide a chance pelo fator."""
    nota = np.asarray(nota, dtype=float)
    return nota / (nota + fator * (1 - nota))


def corte_equivalente(corte, fator):
    """O corte na nota sem correção que dá a mesma lista que o corte na nota corrigida."""
    return fator * corte / (fator * corte + 1 - corte)


# ---------------------------------------------------------------- medidas

def medir(y, nota, corte, peso=None):
    y = np.asarray(y).astype(int)
    liga = np.asarray(nota) > corte
    w = np.ones(len(y)) if peso is None else np.asarray(peso, dtype=float)
    vp, fp = w[liga & (y == 1)].sum(), w[liga & (y == 0)].sum()
    fn = w[~liga & (y == 1)].sum()
    lig = vp + fp
    return {"pedidos": w.sum(), "ligacoes": lig, "parte": lig / w.sum(),
            "precisao": vp / lig if lig else None, "revocacao": vp / (vp + fn),
            "custo": LIGACAO * lig + CANCELAMENTO * fn, "cabe": lig <= TETO * w.sum()}


def modelo_de_vizinhos(x_treino, y_treino, x_teste):
    """A nota de cada linha do teste é a parte de cancelados entre os 5 vizinhos dela no treino."""
    viz = vizinhos_de(np.asarray(x_teste, float), np.asarray(x_treino, float), VIZINHOS)
    return np.asarray(y_treino)[viz].mean(axis=1)


def dobras_estratificadas(y, k, rng):
    y = np.asarray(y)
    dobra = np.empty(len(y), dtype=int)
    for classe in (0, 1):
        i = np.where(y == classe)[0]
        rng.shuffle(i)
        dobra[i] = np.arange(len(i)) % k
    return dobra


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    return "R$ " + num(x, 0)


# ---------------------------------------------------------------- blocos

def bloco_treino(x_tr, y_tr, proporcao):
    print(f"1. o treino de cada estratégia, levado a {pct(proporcao)} de cancelados")
    print(f"{'estratégia':<17}{'linhas':>7}{'cancel.':>9}{'entreg.':>9}{'% cancel.':>11}   o que mudou")
    fator = fator_da_escala(y_tr, proporcao)
    for e in ESTRATEGIAS:
        x, y, w, origem = rebalancear(x_tr, y_tr, e, proporcao, np.random.default_rng(SORTEIO))
        n1, n0 = int(y.sum()), int(len(y) - y.sum())
        share = y.mean()
        if e == "peso":
            nota = f"cada cancelado pesa {num(w[y == 1][0], 2)}; {pct(w[y == 1].sum() / w.sum())} pelo peso"
        else:
            nota = {"nada": "-",
                    "subamostragem": f"{int(len(y_tr) - y_tr.sum()) - n0} entregues sorteados saem",
                    "sobreamostragem": f"{n1 - int(y_tr.sum())} cópias de cancelados sorteados",
                    "SMOTE": f"{n1 - int(y_tr.sum())} cancelados novos, entre um cancelado e um vizinho"}[e]
        print(f"{e:<17}{len(y):>7}{n1:>9}{n0:>9}{pct(share):>11}   {nota}")
        if e == "SMOTE":
            novos = x.iloc[len(y_tr):]
            dummies = [c for c in x.columns if c.startswith(("categoria_", "forma_pagamento_", "canal_"))]
            quebrado = ((novos[dummies] > 0) & (novos[dummies] < 1)).any(axis=1)
            pagamento = [c for c in dummies if c.startswith("forma_pagamento_")]
            exemplo = novos[((novos[pagamento] >= 0.1) & (novos[pagamento] <= 0.9)).any(axis=1)].iloc[0]
            partes = [f"{c[len('forma_pagamento_'):]} {num(exemplo[c], 2)}" for c in pagamento if exemplo[c] > 0]
            print(f"{'':<17}cancelados novos com categoria, pagamento ou canal pela metade: "
                  f"{int(quebrado.sum())} de {len(novos)}")
            print(f"{'':<17}o primeiro deles paga com {' e '.join(partes)}")
    print(f"   fator da escala: a chance de cancelar no treino ficou {num(fator, 2)} vezes maior")
    return fator


def bloco_validacao(x_tr, y_tr, x_va, y_va, proporcao, fator):
    import classificador
    corte_eq = corte_equivalente(EMPATE, fator)
    linhas = {}
    for e in ESTRATEGIAS:
        x, y, w, _ = rebalancear(x_tr, y_tr, e, proporcao, np.random.default_rng(SORTEIO))
        modelo = treinar_com_peso(x, y, w) if e == "peso" else classificador.treinar(x, pd.Series(y))
        linhas[e] = classificador.nota(modelo, x_va).to_numpy()
    cab = (f"{'estratégia':<17}{'nota média':>11}{'ligações':>10}{'% pedidos':>10}{'precisão':>10}"
           f"{'revocação':>11}{'custo':>10}{'cabe?':>7}")

    def linha(e, nota, corte):
        m = medir(y_va, nota, corte)
        print(f"{e:<17}{pct(nota.mean()):>11}{int(m['ligacoes']):>10}{pct(m['parte']):>10}"
              f"{pct(m['precisao']):>10}{pct(m['revocacao']):>11}{reais(m['custo']):>10}"
              f"{'sim' if m['cabe'] else 'não':>7}")

    print(f"2. a validação como chega: {len(y_va)} pedidos, {pct(y_va.mean())} cancelados; "
          f"liga quando a nota passa de {num(EMPATE, 3)}")
    print(cab)
    for e in ESTRATEGIAS:
        linha(e, linhas[e], EMPATE)
    print(f"   acerto do par: " + "; ".join(f"{e} {pct(classificador.acerto_do_par(linhas[e], y_va))}"
                                           for e in ESTRATEGIAS))
    print()
    print(f"3. a mesma validação, com a nota corrigida pelo fator {num(fator, 2)}")
    print(f"   nota corrigida = nota ÷ (nota + {num(fator, 2)} × (1 − nota)); "
          f"é o mesmo que subir o corte de {num(EMPATE, 3)} para {num(corte_eq, 3)}")
    print(cab)
    for e in ESTRATEGIAS:
        linha(e, linhas[e] if e == "nada" else corrigir(linhas[e], fator), EMPATE)
    return linhas


def bloco_dobras(x_tr, y_tr, proporcao):
    import classificador
    print(f"4. reamostrar dentro ou fora das dobras: 5 dobras estratificadas nos {len(y_tr)} pedidos do treino")
    print("   dentro: separa as dobras e reamostra só a parte de treino de cada uma")
    print("   fora: reamostra os pedidos do treino inteiros e depois separa as dobras")
    print(f"{'como':<24}{'% cancel. no teste':>19}{'parente no treino':>19}{'classificador':>15}{'vizinhos':>10}")
    print(f"{'':<24}{'':>19}{'(cancelados)':>19}{'acerto do par':>15}{'(5)':>10}")
    y_tr = np.asarray(y_tr).astype(int)
    x_tr = x_tr.reset_index(drop=True)
    for e, onde in [("nada", "-"), ("sobreamostragem", "dentro"), ("sobreamostragem", "fora"),
                    ("SMOTE", "dentro"), ("SMOTE", "fora")]:
        rng = np.random.default_rng(SORTEIO)
        if onde == "fora":
            x_all, y_all, _, origem = rebalancear(x_tr, y_tr, e, proporcao, rng)
            x_all = x_all.reset_index(drop=True)
        else:
            x_all, y_all, origem = x_tr, y_tr, np.c_[np.arange(len(y_tr)), np.arange(len(y_tr))]
        dobra = dobras_estratificadas(y_all, 5, np.random.default_rng(1))
        par_c, par_v, share, parentes, cancel_teste = [], [], [], 0, 0
        for d in range(5):
            te, tr = dobra == d, dobra != d
            x_t, y_t, o_t = x_all[tr], y_all[tr], origem[tr]
            if onde == "dentro":
                x_t, y_t, _, o_loc = rebalancear(x_t.reset_index(drop=True), y_t, e, proporcao, rng)
                o_t = np.where(tr)[0][o_loc]                  # de volta aos pedidos do treino
            x_t = x_t.reset_index(drop=True)
            modelo = classificador.treinar(x_t, pd.Series(y_t))
            x_te = x_all[te].reset_index(drop=True)
            par_c.append(classificador.acerto_do_par(classificador.nota(modelo, x_te), y_all[te]))
            par_v.append(classificador.acerto_do_par(modelo_de_vizinhos(x_t, y_t, x_te), y_all[te]))
            share.append(y_all[te].mean())
            no_treino = set(o_t[:, 0]) | set(o_t[:, 1])
            for pais in origem[te][y_all[te] == 1]:
                cancel_teste += 1
                parentes += int(pais[0] in no_treino or pais[1] in no_treino)
        rotulo = e if onde == "-" else f"{e}, {onde}"
        print(f"{rotulo:<24}{pct(np.mean(share)):>19}{f'{parentes} de {cancel_teste}':>19}"
              f"{pct(np.mean(par_c)):>15}{pct(np.mean(par_v)):>10}")
    print("   parente: o mesmo pedido, uma cópia dele ou um cancelado novo feito a partir dele")


def bloco_teste_reamostrado(x_tr, y_tr, x_va, y_va, proporcao):
    import classificador
    y_va = np.asarray(y_va).astype(int)
    pos = np.where(y_va == 1)[0]
    novos = int((y_va == 0).sum() - len(pos))
    linhas, _ = smote(x_va.to_numpy(float)[pos], novos, VIZINHOS, np.random.default_rng(SORTEIO + 1))
    x_bal = pd.concat([x_va.reset_index(drop=True), pd.DataFrame(linhas, columns=x_va.columns)],
                      ignore_index=True)
    y_bal = np.r_[y_va, np.ones(novos, int)]
    x, y, _, _ = rebalancear(x_tr, y_tr, "SMOTE", proporcao, np.random.default_rng(SORTEIO))
    m_smote = classificador.treinar(x, pd.Series(y))
    m_nada = classificador.treinar(x_tr, y_tr)
    print(f"5. a validação reamostrada: SMOTE também nos pedidos de abril e maio, até 50% de cancelados")
    print(f"{'modelo, corte':<22}{'validação':<14}{'pedidos':>8}{'% cancel.':>10}{'ligações':>9}"
          f"{'% pedidos':>10}{'precisão':>10}{'revocação':>11}{'40 e 40?':>9}{'cabe?':>7}")
    for nome, modelo, corte in [("SMOTE, corte 0,5", m_smote, 0.5),
                                (f"nada, corte {num(EMPATE, 3)}", m_nada, EMPATE)]:
        for rot, xv, yv in [("com SMOTE", x_bal, y_bal), ("como chega", x_va, y_va)]:
            m = medir(yv, classificador.nota(modelo, xv).to_numpy(), corte)
            regua = (m["precisao"] or 0) >= REGUA and m["revocacao"] >= REGUA
            print(f"{nome:<22}{rot:<14}{int(m['pedidos']):>8}{pct(yv.mean()):>10}{int(m['ligacoes']):>9}"
                  f"{pct(m['parte']):>10}{pct(m['precisao']):>10}{pct(m['revocacao']):>11}"
                  f"{'sim' if regua else 'não':>9}{'sim' if m['cabe'] else 'não':>7}")
    print(f"   40 e 40: precisão e revocação de pelo menos {pct(REGUA)}; cabe: no máximo 1 ligação para cada 4 pedidos")
    print("   o custo fica de fora: com cancelados inventados, R$ deixa de ser dinheiro da loja")


def bloco_outro_mes(x_tr, y_tr, x_va, y_va, prevalencia):
    import classificador
    y = np.asarray(y_va).astype(int)
    nota = classificador.nota(classificador.treinar(x_tr, y_tr), x_va).to_numpy()
    peso = np.where(y == 1, prevalencia / (1 - prevalencia) * (y == 0).sum() / (y == 1).sum(), 1.0)
    print(f"6. outro mês: a validação pesada para {pct(prevalencia)} de cancelados (estratégia nada, "
          f"corte {num(EMPATE, 3)})")
    print("   cada cancelado vale por vários pedidos; a validação segue com os mesmos 795, só o peso muda")
    print(f"{'mês':<20}{'% cancel.':>10}{'nota média':>11}{'% pedidos ligados':>18}{'precisão':>10}{'revocação':>11}")
    for rot, w in [("abril e maio", None), (f"com {pct(prevalencia)}", peso)]:
        m = medir(y, nota, EMPATE, w)
        share = y.mean() if w is None else w[y == 1].sum() / w.sum()
        media = nota.mean() if w is None else float((nota * w).sum() / w.sum())
        print(f"{rot:<20}{pct(share):>10}{pct(media):>11}{pct(m['parte']):>18}{pct(m['precisao']):>10}"
              f"{pct(m['revocacao']):>11}")


def proporcao_valida(texto):
    try:
        q = float(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{texto!r} não é um número; use, por exemplo, 0.33")
    if not 0.25 <= q <= 0.5:
        raise argparse.ArgumentTypeError("a proporção vai de 0.25 a 0.5 (o treino já tem 19,8%)")
    return q


def prevalencia_valida(texto):
    try:
        p = float(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{texto!r} não é um número; use, por exemplo, 0.30")
    if not 0.05 <= p <= 0.6:
        raise argparse.ArgumentTypeError("a prevalência vai de 0.05 a 0.6")
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pesos, sub e sobreamostragem e SMOTE nos pedidos.")
    ap.add_argument("--proporcao", type=proporcao_valida, default=0.5,
                    help="parte de cancelados no treino depois da estratégia (0.25 a 0.5; padrão 0.5)")
    ap.add_argument("--prevalencia", type=prevalencia_valida, default=None,
                    help="acrescenta o bloco 6: a validação pesada para essa parte de cancelados")
    args = ap.parse_args(argv)
    if not BASE.is_file() or not Path("classificador.py").is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 13-desbalanceamento-e-prevalencia do kit.")
    import pipeline_corrigido
    base = pd.read_csv(BASE, parse_dates=["data_pedido"])
    x_tr, y_tr, x_va, y_va = pipeline_corrigido.preparar(base)
    print(f"treino: {len(y_tr)} pedidos de janeiro a março, {int(y_tr.sum())} cancelados ({pct(y_tr.mean())})")
    print(f"validação: {len(y_va)} pedidos de abril e maio, {int(y_va.sum())} cancelados ({pct(y_va.mean())})")
    print("junho, o teste, fica fora: nenhuma estratégia toca nele")
    print()
    fator = bloco_treino(x_tr, y_tr, args.proporcao)
    print()
    bloco_validacao(x_tr, y_tr, x_va, y_va, args.proporcao, fator)
    print()
    bloco_dobras(x_tr, y_tr, args.proporcao)
    print()
    bloco_teste_reamostrado(x_tr, y_tr, x_va, y_va, args.proporcao)
    if args.prevalencia is not None:
        print()
        bloco_outro_mes(x_tr, y_tr, x_va, y_va, args.prevalencia)


if __name__ == "__main__":
    main()
