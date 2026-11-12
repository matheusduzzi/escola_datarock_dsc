"""As curvas de aprendizado da aula «Curvas de aprendizado» do curso ML: preparação e validação.

    python3 curva.py                  # os pedidos: três modelos, do mais pobre ao mais rico
    python3 curva.py --caso pessoas   # o exercício: as admissões do acompanhamento do RH

Uma curva de aprendizado treina o mesmo modelo em fatias cada vez maiores do treino e mede, em
cada fatia, o acerto do par em dois lugares: nos próprios dados que o modelo viu (treino) e na
validação, que é sempre a mesma. Cada tamanho menor que o treino inteiro é sorteado 20 vezes.

Em cada fatia, a preparação é ajustada só nas linhas da fatia, como manda a aula 10. O teste
(junho, nos pedidos; outubro a dezembro de 2025, nas admissões) sai na leitura e não entra em
nenhuma conta.

A saída tem três blocos:
  1. a curva de cada modelo: treino, validação, a distância entre os dois e a faixa da validação
     entre os 20 sorteios de cada tamanho;
  2. de onde vem a distância do modelo do meio: o próprio treino, cinco dobras dentro do período
     do treino, a validação e cada mês da validação;
  3. quanto a própria validação varia: a faixa de 90% de cada modelo e da diferença contra o
     modelo do meio, refazendo a conta em 1000 sorteios com reposição das linhas da validação.
     Os modelos não mudam; só a validação é sorteada de novo, para medir a incerteza dela.
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

SORTEIOS_FATIA = 20
SORTEIOS_VALIDACAO = 1000
DOBRAS = 5
SORTEIO = 12            # o mesmo sorteio toda vez: a saída não muda de uma rodada para outra


# ---------------------------------------------------------------- os dois casos

class Pedidos:
    nome = "pedidos"
    unidade = "pedidos"
    os = "os"
    rotulo1 = "cancelados"
    proprios = "nos próprios pedidos do treino"
    nao_viu = "em pedidos do treino que ele não viu"
    pasta = Path("../dados/loja/pedidos_export_completo.csv")
    tamanhos = [100, 200, 300, 500, 800]
    alvo = "cancelado"
    descricao_treino = "janeiro a março de 2026"
    descricao_validacao = "abril e maio de 2026"
    descricao_teste = "junho, o teste, fica fora"
    PARES = [("categoria", "forma_pagamento"), ("categoria", "canal"), ("forma_pagamento", "canal"),
             ("categoria", "cliente_novo"), ("forma_pagamento", "cliente_novo"),
             ("categoria", "prazo_prometido_dias")]
    modelos = ["só o pagamento", "o classificador da aula 10", "com as combinações"]
    meio = "o classificador da aula 10"

    def carregar(self):
        import pipeline_corrigido as pc
        self.pc = pc
        base = pd.read_csv(self.pasta, parse_dates=["data_pedido"])
        base = base[base["data_pedido"] <= pd.Timestamp(pc.FIM_VALIDACAO)]       # junho sai aqui
        treino = base[base["data_pedido"] <= pd.Timestamp(pc.FIM_TREINO)].reset_index(drop=True)
        validacao = base[base["data_pedido"] > pd.Timestamp(pc.FIM_TREINO)].reset_index(drop=True)
        return treino, validacao

    def mes(self, d):
        return d["data_pedido"].dt.strftime("%Y-%m")

    def ajustar(self, fatia, modelo):
        params = self.pc.ajustar(fatia)
        if modelo == "com as combinações":
            params["pares"] = {par: sorted(_chave(fatia, par).unique()) for par in self.PARES}
        return params

    def tabela(self, params, d, modelo):
        y = d[self.alvo].to_numpy(dtype=int)
        if modelo == "só o pagamento":
            x = pd.DataFrame({f"forma_pagamento_{v}": (d["forma_pagamento"] == v).astype(float)
                              for v in params["categorias"]["forma_pagamento"]})
            return x, y
        x = self.pc.aplicar(params, d).reset_index(drop=True)
        if modelo == "com as combinações":
            x = _com_pares(x, d, params["pares"])
        return x, y


class Pessoas:
    nome = "pessoas"
    unidade = "pessoas"
    os = "as"
    rotulo1 = "saíram antes de 180 dias"
    proprios = "nas próprias pessoas do treino"
    nao_viu = "em pessoas do treino que ele não viu"
    pasta = Path("../dados/pessoas/admissoes.csv")
    tamanhos = [100, 200, 300, 500]
    alvo = "saiu_180d"
    descricao_treino = "admitidas até 30/06/2025"
    descricao_validacao = "admitidas de julho a setembro de 2025"
    descricao_teste = "o teste fica fechado"
    PARES = [("loja", "cargo"), ("loja", "turno"), ("cargo", "turno")]
    modelos = ["só o cargo", "o pipeline da aula 09", "com as combinações"]
    meio = "o pipeline da aula 09"

    def carregar(self):
        import pipeline_pessoas as pp
        self.pp = pp
        treino, validacao, _, _ = pp.separar(pp.carregar(self.pasta))   # o teste sai aqui
        return treino.reset_index(drop=True), validacao.reset_index(drop=True)

    def mes(self, d):
        return d["data_admissao"].dt.strftime("%Y-%m")

    def ajustar(self, fatia, modelo):
        params = self.pp.ajustar(fatia)
        if modelo == "com as combinações":
            params["pares"] = {par: sorted(_chave(fatia, par).unique()) for par in self.PARES}
        return params

    def tabela(self, params, d, modelo):
        x = self.pp.aplicar(params, d).reset_index(drop=True)
        liberada = x["liberada"].to_numpy(dtype=bool)
        if not liberada.all():                 # a curva só usa quem o pipeline libera
            raise ValueError(f"{int((~liberada).sum())} pessoas sem nota: o pipeline não liberou")
        cols = params["colunas"]
        if modelo == "só o cargo":
            cols = [c for c in cols if c.startswith("cargo_")]
        x = x[cols]
        if modelo == "com as combinações":
            x = _com_pares(x, d, params["pares"])
        return x, d[self.alvo].to_numpy(dtype=int)


def _chave(d, par):
    a, b = par
    return d[a].astype(str) + "|" + d[b].astype(str)


def _com_pares(x, d, pares):
    """Uma coluna de 0 e 1 para cada combinação de duas categorias que a fatia do treino tem."""
    novas = {}
    for par, valores in pares.items():
        chave = _chave(d, par).to_numpy()
        for v in valores:
            novas[f"{par[0]}+{par[1]}={v}"] = (chave == v).astype(float)
    return pd.concat([x.reset_index(drop=True), pd.DataFrame(novas)], axis=1)


# ---------------------------------------------------------------- as contas

def treinar_e_medir(caso, fatia, validacao, modelo, clf):
    params = caso.ajustar(fatia, modelo)
    x_tr, y_tr = caso.tabela(params, fatia, modelo)
    x_va, y_va = caso.tabela(params, validacao, modelo)
    m = clf.treinar(x_tr, y_tr)
    nota_va = clf.nota(m, x_va).to_numpy()
    return clf.acerto_do_par(clf.nota(m, x_tr), y_tr), clf.acerto_do_par(nota_va, y_va), nota_va, x_tr.shape[1]


def curva(caso, treino, validacao, modelo, clf, rng):
    linhas = []
    for n in caso.tamanhos + [len(treino)]:
        vezes = SORTEIOS_FATIA if n < len(treino) else 1
        tr, va = [], []
        for _ in range(vezes):
            fatia = treino if n == len(treino) else treino.iloc[np.sort(rng.choice(len(treino), n, replace=False))]
            a_tr, a_va, _, colunas = treinar_e_medir(caso, fatia, validacao, modelo, clf)
            tr.append(a_tr)
            va.append(a_va)
        linhas.append({"n": n, "vezes": vezes, "treino": np.mean(tr), "validacao": np.mean(va),
                       "min": min(va), "max": max(va), "colunas": colunas})
    return linhas


def dobras(caso, treino, modelo, clf, rng):
    """Cinco dobras sorteadas dentro do período do treino: o modelo nunca vê a dobra que mede."""
    ordem = rng.permutation(len(treino))
    resultado = []
    for parte in np.array_split(ordem, DOBRAS):
        dentro = treino.iloc[np.sort(np.setdiff1d(ordem, parte))]
        fora = treino.iloc[np.sort(parte)]
        resultado.append(treinar_e_medir(caso, dentro, fora, modelo, clf)[1])
    return resultado


def faixa_validacao(notas, y, clf, rng):
    """Faixa de 90% de cada modelo e da diferença contra o do meio, nos mesmos sorteios."""
    nomes = list(notas)
    contas = {k: [] for k in nomes}
    for _ in range(SORTEIOS_VALIDACAO):
        i = rng.integers(0, len(y), len(y))
        for k in nomes:
            contas[k].append(clf.acerto_do_par(notas[k][i], y[i]))
    return {k: np.array(v) for k, v in contas.items()}


# ---------------------------------------------------------------- saída

def num(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return num(100 * x) + "%"


def pontos(x):
    return ("+" if x > 0.0005 else "") + num(100 * x)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--caso", choices=["pedidos", "pessoas"], default="pedidos")
    args = ap.parse_args()
    caso = Pedidos() if args.caso == "pedidos" else Pessoas()
    if not caso.pasta.is_file() or not Path("classificador.py").is_file():
        sys.exit(f"não achei {caso.pasta}. Rode de dentro da pasta 12-curvas-de-aprendizado do kit.")
    import classificador as clf
    warnings.simplefilter("ignore")
    rng = np.random.default_rng(SORTEIO)
    treino, validacao = caso.carregar()
    y_va = validacao[caso.alvo].to_numpy(dtype=int)

    print(f"treino: {len(treino)} {caso.unidade} ({caso.descricao_treino}); "
          f"validação: {len(validacao)} ({caso.descricao_validacao}), {int(y_va.sum())} {caso.rotulo1} "
          f"({pct(y_va.mean())}); {caso.descricao_teste}")
    print(f"medida: acerto do par; cada tamanho menor que {len(treino)} é sorteado {SORTEIOS_FATIA} vezes")

    print("\n1. a curva de cada modelo")
    print(f"{'tamanho':>8} {'treino':>7} {'validação':>10} {'distância':>10}   faixa da validação nos sorteios")
    for modelo in caso.modelos:
        linhas = curva(caso, treino, validacao, modelo, clf, rng)
        print(f"{modelo} ({linhas[-1]['colunas']} colunas no treino inteiro)")
        for l in linhas:
            faixa = f"{pct(l['min'])} a {pct(l['max'])}" if l["vezes"] > 1 else "uma rodada só"
            print(f"{l['n']:>8} {pct(l['treino']):>7} {pct(l['validacao']):>10} "
                  f"{pontos(l['treino'] - l['validacao']):>10}   {faixa}")

    print(f"\n2. de onde vem a distância: {caso.meio}, treinado com {caso.os} {len(treino)}")
    a_tr, a_va, _, _ = treinar_e_medir(caso, treino, validacao, caso.meio, clf)
    d = dobras(caso, treino, caso.meio, clf, rng)
    largura = len(caso.nao_viu) + 1
    print(f"{caso.proprios + ':':<{largura}} {pct(a_tr):>6}")
    print(f"{caso.nao_viu + ':':<{largura}} {pct(np.mean(d)):>6}   "
          f"(média de {DOBRAS} dobras: {', '.join(pct(v) for v in d)})")
    print(f"{'na validação:':<{largura}} {pct(a_va):>6}")
    for mes, g in validacao.groupby(caso.mes(validacao)):
        params = caso.ajustar(treino, caso.meio)
        x_tr, y_tr = caso.tabela(params, treino, caso.meio)
        x_g, y_g = caso.tabela(params, g.reset_index(drop=True), caso.meio)
        m = clf.treinar(x_tr, y_tr)
        print(f"   {mes}: {len(g):>4} {caso.unidade}, {int(y_g.sum()):>3} {caso.rotulo1}, "
              f"acerto do par {pct(clf.acerto_do_par(clf.nota(m, x_g), y_g))}")

    print(f"\n3. quanto a validação varia: {SORTEIOS_VALIDACAO} sorteios com reposição d{caso.os} "
          f"{len(validacao)} {caso.unidade}, modelos treinados com {caso.os} {len(treino)}")
    notas = {modelo: treinar_e_medir(caso, treino, validacao, modelo, clf)[2] for modelo in caso.modelos}
    contas = faixa_validacao(notas, y_va, clf, rng)
    print(f"{'modelo':<28} {'na validação':>12}   {'faixa de 90%':<16}   diferença contra {caso.meio}")
    for modelo in caso.modelos:
        a = clf.acerto_do_par(notas[modelo], y_va)
        lo, hi = np.percentile(contas[modelo], [5, 95])
        if modelo == caso.meio:
            dif = "-"
        else:
            dl, dh = np.percentile(contas[modelo] - contas[caso.meio], [5, 95])
            base = clf.acerto_do_par(notas[caso.meio], y_va)
            dif = f"{pontos(a - base)} pontos, faixa {pontos(dl)} a {pontos(dh)}"
        print(f"{modelo:<28} {pct(a):>12}   {pct(lo) + ' a ' + pct(hi):<16}   {dif}")


if __name__ == "__main__":
    main()
