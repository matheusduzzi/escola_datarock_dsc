"""O exercício: a auditoria do modelo do acompanhamento da consultoria, nos mesmos quatro passos.

Aula «Auditoria de um pipeline» do curso ML: preparação e validação. Rode de dentro da pasta da aula:

    python3 auditar_rh.py reproduzir   # pronto: roda o projeto deles sem mudar nada
    python3 auditar_rh.py achados      # depois de escrever as três checar_*() de achados_rh.py
    python3 auditar_rh.py consertos    # depois de escrever o preparar() de consertar_rh.py
    python3 auditar_rh.py checar       # refaz tudo e compara com o manifesto

Cada passo grava a sua saída em auditoria_rh/ e põe a impressão digital das entradas e da saída
em auditoria_rh/manifesto.json. A referência é o pipeline da aula 09 (pipeline_pessoas.py), com a
mesma divisão: treino até 2025-06-30, medida na validação. O teste do acompanhamento não é usado:
ele já foi aberto uma vez, na aula 16.
"""
import sys
from pathlib import Path

import pandas as pd

BASE = Path("../dados/pessoas/admissoes.csv")
LEIA_ME = Path("consultoria-LEIA-ME.md")
PASTA = Path("auditoria_rh")
CORTE = 0.32
ACERTO, ACOMPANHAMENTO = 750, 240        # R$ 3.000 × 1/4 por saída evitada; R$ 240 por acompanhamento
COMUM = [BASE, "auditar_rh.py", "auditoria.py", "classificador.py", "consultoria_acompanhamento.py"]
ENTRADAS = {"reproduzir": COMUM + [LEIA_ME],
            "achados": COMUM + ["achados_rh.py", "consertar_rh.py", "pipeline_pessoas.py"],
            "consertos": COMUM + ["consertar_rh.py", "pipeline_pessoas.py"]}

_faltam = [str(a) for a in [BASE, LEIA_ME, "consultoria_acompanhamento.py", "achados_rh.py", "consertar_rh.py",
                            "pipeline_pessoas.py", "auditoria.py", "classificador.py"] if not Path(a).is_file()]
if _faltam:
    sys.exit(f"não achei {', '.join(_faltam)}. Rode de dentro da pasta 17-auditoria-de-um-pipeline do kit.")

import achados_rh  # noqa: E402
import consertar_rh  # noqa: E402
import consultoria_acompanhamento as consultoria  # noqa: E402
import pipeline_pessoas as pp  # noqa: E402
from auditoria import Manifesto, digital, medir, pct, reais  # noqa: E402
from classificador import nota, treinar  # noqa: E402


def ler():
    return pd.read_csv(BASE, parse_dates=["data_admissao", "data_desligamento"])


def referencia(base):
    """O pipeline da aula 09 com a mesma saída dos outros: treino e validação, com o id no índice."""
    treino, validacao, _, _ = pp.separar(base)
    params = pp.ajustar(treino)
    saida = []
    for parte in (treino, validacao):
        x = pp.aplicar(params, parte)[params["colunas"]]
        saida += [x, parte.set_index("id_pessoa").loc[x.index, "saiu_180d"].astype(int)]
    return tuple(saida)


PIPELINES = {"consultoria": consultoria.preparar, "consertar_rh": consertar_rh.preparar,
             "pipeline da aula 09": referencia}


def rodar(preparar, base):
    x_tr, y_tr, x_me, y_me = preparar(base)
    s = nota(treinar(x_tr, y_tr), x_me)
    return x_tr, y_tr, x_me, y_me, medir(y_me, s, CORTE, ACERTO, ACOMPANHAMENTO)


def texto_reproduzir():
    base = ler()
    leia_me = LEIA_ME.read_text(encoding="utf-8")
    dig_base = digital(BASE)[:12]
    x_tr, _, x_te, _, m = rodar(consultoria.preparar, base)
    resultado = f"acerto do par {pct(m['acerto_do_par'])}"
    return "\n".join([
        f"projeto: consultoria_acompanhamento.py, impressão digital {digital('consultoria_acompanhamento.py')[:12]}",
        f"base: {BASE.as_posix()}, impressão digital {dig_base}",
        f"  a base do LEIA-ME da consultoria: {'a mesma' if dig_base in leia_me else 'outra'}",
        "o preparar() da consultoria e o classificador do curso, sem mudar nada:",
        f"  treino: {len(x_tr)} pessoas; teste: {len(x_te)} pessoas, {m['positivos']} com rótulo 1",
        f"  lista com corte 0,32: {m['lista']} pessoas, {m['vp']} certas",
        f"  {resultado}",
        f"  o LEIA-ME da consultoria diz o mesmo: {'sim' if resultado in leia_me else 'não'}",
    ]) + "\n"


def texto_achados():
    base = ler()
    saidas = {nome: p(base) for nome, p in PIPELINES.items()}
    linhas = ["três perguntas, feitas ao preparar() da consultoria, ao seu conserto e ao da aula 09", "",
              "1. alvo: cada pessoa e cada rótulo seguem o contrato da aula 03?",
              f"  {'pipeline':<24}{'saiu até o dia 7':>18}{'depois de 01/01':>17}{'fora do contrato':>18}"
              f"{'rótulo diferente':>18}"]
    for nome, (x_tr, y_tr, x_me, y_me) in saidas.items():
        a = achados_rh.checar_alvo(base, pd.concat([y_tr, y_me]))
        linhas.append(f"  {nome:<24}{a['saiu_ate_o_dia_7']:>18}{a['depois_de_2026_01_01']:>17}"
                      f"{a['fora_do_contrato']:>18}{a['rotulo_diferente']:>18}")
    linhas += ["", "2. divisão: o treino vem antes do que se mede? o teste fica de fora?",
               f"  {'pipeline':<24}{'treino depois':>18}{'teste no treino':>18}"]
    for nome, (x_tr, y_tr, x_me, y_me) in saidas.items():
        d = achados_rh.checar_divisao(base, x_tr.index, x_me.index)
        linhas.append(f"  {nome:<24}{d['treino_depois_do_inicio']:>18}{d['teste_no_treino']:>18}")
    linhas += ["", "3. transformação: mexer só no que se mede muda o resto?",
               f"  {'pipeline':<24}{'resultado: treino':>19}{'resultado: medida':>19}{'distância: treino':>19}"]
    for nome, p in PIPELINES.items():
        t = achados_rh.checar_transformacao(base, p)
        linhas.append(f"  {nome:<24}{t['treino_com_resultado']:>19}{t['medida_com_resultado']:>19}"
                      f"{t['treino_com_distancia']:>19}")
    return "\n".join(linhas) + "\n"


def texto_consertos():
    base = ler()
    passos = [("consultoria, como entregue", "30% sorteadas", consultoria.preparar),
              ("com os três consertos", "julho a setembro", consertar_rh.preparar),
              ("pipeline da aula 09", "julho a setembro", referencia)]
    linhas = ["o mesmo classificador e o mesmo corte, 0,32", "",
              f"{'pipeline':<28}{'medido em':<18}{'pessoas':>8}{'saíram':>7}{'marcadas':>9}{'certas':>7}"
              f"{'precisão':>10}{'revocação':>10}{'acerto do par':>14}{'saldo':>11}"]
    for nome, onde, p in passos:
        m = rodar(p, base)[4]
        linhas.append(f"{nome:<28}{onde:<18}{m['n']:>8}{m['positivos']:>7}{m['lista']:>9}{m['vp']:>7}"
                      f"{pct(m['precisao']):>10}{pct(m['revocacao']):>10}{pct(m['acerto_do_par']):>14}"
                      f"{reais(m['saldo']):>11}")
    linhas += ["", "saldo contra não acompanhar ninguém: R$ 750 por saída evitada, R$ 240 por acompanhamento",
               "saldo só compara linhas medidas nas mesmas pessoas"]
    return "\n".join(linhas) + "\n"


PASSOS = {"reproduzir": ("reproducao.txt", texto_reproduzir), "achados": ("achados.txt", texto_achados),
          "consertos": ("consertos.txt", texto_consertos)}


def main():
    pedido = sys.argv[1] if len(sys.argv) > 1 else ""
    manifesto = Manifesto(PASTA)
    try:
        if pedido in PASSOS:
            nome, funcao = PASSOS[pedido]
            texto = funcao()
            impressao = manifesto.anotar(ENTRADAS[pedido], nome, texto)
            print(texto, end="")
            print(f"\nanotado em {PASTA.as_posix()}/{nome}; manifesto com impressão digital {impressao}")
        elif pedido == "checar":
            if not manifesto.caminho.is_file():
                sys.exit("ainda não há manifesto. Rode antes: python3 auditar_rh.py reproduzir (e achados, consertos)")
            tudo, texto = manifesto.checar({nome: f for nome, f in PASSOS.values()})
            print(texto)
            if not tudo:
                print("diferente do manifesto: os números do parecer não saem mais desses arquivos", file=sys.stderr)
                sys.exit(1)
            print("tudo igual: quem rodar esses arquivos chega aos mesmos números")
        else:
            sys.exit("use: python3 auditar_rh.py reproduzir | achados | consertos | checar")
    except NotImplementedError as falta:
        sys.exit(f"{falta}. Nada foi anotado em {PASTA.as_posix()}/.")


if __name__ == "__main__":
    main()
