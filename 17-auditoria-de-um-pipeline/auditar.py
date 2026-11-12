"""A auditoria do modelo de cancelamento da consultoria, em quatro passos.

Aula «Auditoria de um pipeline» do curso ML: preparação e validação. Rode de dentro da pasta da aula:

    python3 auditar.py reproduzir   # roda o projeto deles sem mudar nada e compara com o LEIA-ME deles
    python3 auditar.py achados      # as três perguntas: alvo, divisão e transformação
    python3 auditar.py consertos    # um conserto de cada vez, somados, medidos em abril e maio
    python3 auditar.py checar       # refaz tudo e compara com o manifesto

Cada passo grava a sua saída em auditoria/ e põe a impressão digital das entradas e da saída em
auditoria/manifesto.json. O checar refaz os três passos e diz o que mudou. O teste de junho não
é usado: ele já foi aberto uma vez, na aula 16.
"""
import sys
from pathlib import Path

import pandas as pd

BASE = Path("../dados/loja/pedidos_export_completo.csv")
LEIA_ME = Path("consultoria-LEIA-ME.md")
PASTA = Path("auditoria")
CORTE = 5 / 15
LIGACAO, CANCELAMENTO = 5, 15
JUNHO = pd.Timestamp("2026-06-01")
COMUM = [BASE, "auditar.py", "auditoria.py", "classificador.py", "consultoria_cancelamento.py"]
ENTRADAS = {"reproduzir": COMUM + [LEIA_ME], "achados": COMUM + ["consertos.py", "pipeline_corrigido.py"],
            "consertos": COMUM + ["consertos.py", "pipeline_corrigido.py"]}

_faltam = [str(a) for a in [BASE, LEIA_ME, "consultoria_cancelamento.py", "consertos.py", "pipeline_corrigido.py",
                            "auditoria.py", "classificador.py"] if not Path(a).is_file()]
if _faltam:
    sys.exit(f"não achei {', '.join(_faltam)}. Rode de dentro da pasta 17-auditoria-de-um-pipeline do kit.")

import consertos  # noqa: E402
import consultoria_cancelamento as consultoria  # noqa: E402
import pipeline_corrigido  # noqa: E402
from auditoria import Manifesto, digital, linhas_que_mudaram, medir, num, pct, reais  # noqa: E402
from classificador import nota, treinar  # noqa: E402

PIPELINES = {"consultoria": consultoria.preparar, "consertos.com_tudo": consertos.com_tudo,
             "pipeline_corrigido (aula 10)": pipeline_corrigido.preparar}


def ler():
    return pd.read_csv(BASE, parse_dates=["data_pedido"])


def rodar(preparar, base):
    x_tr, y_tr, x_te, y_te = preparar(base)
    s = nota(treinar(x_tr, y_tr), x_te)
    return x_tr, y_tr, x_te, y_te, medir(y_te, s, CORTE)


# ---------------------------------------------------------------- as três perguntas

def checar_alvo(base, y):
    """O rótulo de cada pedido contra a coluna cancelado, que é o rótulo do contrato."""
    certo = base.set_index("id_pedido").loc[y.index, "cancelado"].to_numpy()
    dado = y.to_numpy()
    return {"diferentes": int((dado != certo).sum()),
            "cancelados_com_0": int(((dado == 0) & (certo == 1)).sum()),
            "entregues_com_1": int(((dado == 1) & (certo == 0)).sum())}


def checar_divisao(base, ids_treino, ids_medida):
    """As datas do treino e da medida. O treino precisa vir antes, e junho não pode entrar."""
    data = base.set_index("id_pedido")["data_pedido"]
    tr, me = data.loc[ids_treino], data.loc[ids_medida]
    return {"treino": f"{tr.min().date()} a {tr.max().date()}", "medida": f"{me.min().date()} a {me.max().date()}",
            "treino_depois_do_inicio": int((tr >= me.min()).sum()), "junho_no_treino": int((tr >= JUNHO).sum())}


def trocar_resultado(base, ids):
    """Inverte o resultado dos pedidos de ids: quem cancelou foi entregue, e o contrário."""
    b = base.copy()
    m = b["id_pedido"].isin(ids)
    b.loc[m, "cancelado"] = 1 - b.loc[m, "cancelado"]
    b.loc[m, "dias_ate_entrega"] = b.loc[m, "prazo_prometido_dias"].where(b.loc[m, "cancelado"] == 0, 0)
    return b


def trocar_valor(base, ids):
    """Multiplica por 10 o valor dos pedidos de ids."""
    b = base.copy()
    m = b["id_pedido"].isin(ids)
    b.loc[m, "valor"] = b.loc[m, "valor"] * 10
    return b


def checar_transformacao(base, preparar):
    """Mexe só nos pedidos que o pipeline mede e vê o que muda na tabela que o modelo recebe."""
    x_tr, _, x_me, _ = preparar(base)
    a_tr, _, a_me, _ = preparar(trocar_resultado(base, x_me.index))
    b_tr, _, _, _ = preparar(trocar_valor(base, x_me.index))
    return {"treino_com_resultado": linhas_que_mudaram(x_tr, a_tr),
            "medida_com_resultado": linhas_que_mudaram(x_me, a_me),
            "treino_com_valor": linhas_que_mudaram(x_tr, b_tr), "treino": len(x_tr), "medida": len(x_me)}


# ---------------------------------------------------------------- os passos

def texto_reproduzir():
    base = ler()
    leia_me = LEIA_ME.read_text(encoding="utf-8")
    dig_base = digital(BASE)[:12]
    x_tr, y_tr, x_te, y_te, m = rodar(consultoria.preparar, base)
    resultado = (f"precisão {pct(m['precisao'])}, revocação {pct(m['revocacao'])}, "
                 f"acerto do par {pct(m['acerto_do_par'])}")
    return "\n".join([
        f"projeto: consultoria_cancelamento.py, impressão digital {digital('consultoria_cancelamento.py')[:12]}",
        f"base: {BASE.as_posix()}, impressão digital {dig_base}",
        f"  a base do LEIA-ME da consultoria: {'a mesma' if dig_base in leia_me else 'outra'}",
        "o preparar() da consultoria e o classificador do curso, sem mudar nada:",
        f"  treino: {len(x_tr)} pedidos; teste: {len(x_te)} pedidos, {m['positivos']} com rótulo 1",
        f"  lista com corte 0,333: {m['lista']} ligações, {m['vp']} certas",
        f"  {resultado}",
        f"  o LEIA-ME da consultoria diz o mesmo: {'sim' if resultado in leia_me else 'não'}",
    ]) + "\n"


def texto_achados():
    base = ler()
    saidas = {nome: p(base) for nome, p in PIPELINES.items()}
    linhas = ["três perguntas, feitas ao preparar() da consultoria e a dois que não deviam ter defeito", "",
              "1. alvo: o rótulo de cada pedido é o cancelado?",
              f"  {'pipeline':<30}{'diferentes':>11}{'cancelados com 0':>18}{'entregues com 1':>17}"]
    for nome, (x_tr, y_tr, x_te, y_te) in saidas.items():
        a = checar_alvo(base, pd.concat([y_tr, y_te]))
        linhas.append(f"  {nome:<30}{a['diferentes']:>11}{a['cancelados_com_0']:>18}{a['entregues_com_1']:>17}")
    linhas += ["", "2. divisão: o treino vem antes do que se mede? junho fica de fora?",
               f"  {'pipeline':<30}{'treino':>26}{'medida':>26}{'treino depois':>15}{'junho':>7}"]
    for nome, (x_tr, y_tr, x_te, y_te) in saidas.items():
        d = checar_divisao(base, x_tr.index, x_te.index)
        linhas.append(f"  {nome:<30}{d['treino']:>26}{d['medida']:>26}{d['treino_depois_do_inicio']:>15}"
                      f"{d['junho_no_treino']:>7}")
    linhas += ["", "3. transformação: mexer só no que se mede muda o resto?",
               f"  {'pipeline':<30}{'resultado: treino':>19}{'resultado: medida':>19}{'valor: treino':>15}"]
    for nome, p in PIPELINES.items():
        t = checar_transformacao(base, p)
        de = [f"{t['treino_com_resultado']} de {t['treino']}", f"{t['medida_com_resultado']} de {t['medida']}",
              f"{t['treino_com_valor']} de {t['treino']}"]
        linhas.append(f"  {nome:<30}{de[0]:>19}{de[1]:>19}{de[2]:>15}")
    return "\n".join(linhas) + "\n"


def texto_consertos():
    base = ler()
    passos = [("consultoria, como entregue", "30% sorteados", consultoria.preparar),
              ("+ alvo: o cancelado", "30% sorteados", consertos.com_alvo),
              ("+ divisão por data", "abril e maio", consertos.com_alvo_e_divisao),
              ("+ preparação só no treino", "abril e maio", consertos.com_tudo),
              ("a nossa lista (aulas 10 e 11)", "abril e maio", pipeline_corrigido.preparar)]
    linhas = ["o mesmo classificador e o mesmo corte, 0,333; um conserto de cada vez, somados", "",
              f"{'passo':<31}{'medido em':<15}{'pedidos':>8}{'rótulo 1':>9}{'ligações':>9}{'certas':>7}"
              f"{'precisão':>10}{'revocação':>10}{'acerto do par':>14}{'custo':>10}"]
    for nome, onde, p in passos:
        m = rodar(p, base)[4]
        custo = LIGACAO * m["lista"] + CANCELAMENTO * m["fn"]
        linhas.append(f"{nome:<31}{onde:<15}{m['n']:>8}{m['positivos']:>9}{m['lista']:>9}{m['vp']:>7}"
                      f"{pct(m['precisao']):>10}{pct(m['revocacao']):>10}{pct(m['acerto_do_par']):>14}"
                      f"{reais(custo):>10}")
    m = rodar(pipeline_corrigido.preparar, base)[4]
    linhas += ["", f"em abril e maio, não ligar para ninguém custa {reais(CANCELAMENTO * m['positivos'])} "
               f"({m['positivos']} cancelamentos a R$ {CANCELAMENTO})",
               "custo só compara linhas medidas nos mesmos pedidos: as três de abril e maio"]
    return "\n".join(linhas) + "\n"


PASSOS = {"reproduzir": ("reproducao.txt", texto_reproduzir), "achados": ("achados.txt", texto_achados),
          "consertos": ("consertos.txt", texto_consertos)}


def main():
    pedido = sys.argv[1] if len(sys.argv) > 1 else ""
    manifesto = Manifesto(PASTA)
    if pedido in PASSOS:
        nome, funcao = PASSOS[pedido]
        texto = funcao()
        impressao = manifesto.anotar(ENTRADAS[pedido], nome, texto)
        print(texto, end="")
        print(f"\nanotado em {PASTA.as_posix()}/{nome}; manifesto com impressão digital {impressao}")
    elif pedido == "checar":
        if not manifesto.caminho.is_file():
            sys.exit("ainda não há manifesto. Rode antes: python3 auditar.py reproduzir (e achados, consertos)")
        tudo, texto = manifesto.checar({nome: f for nome, f in PASSOS.values()})
        print(texto)
        if not tudo:
            print("diferente do manifesto: os números do parecer não saem mais desses arquivos", file=sys.stderr)
            sys.exit(1)
        print("tudo igual: quem rodar esses arquivos chega aos mesmos números")
    else:
        sys.exit("use: python3 auditar.py reproduzir | achados | consertos | checar")


if __name__ == "__main__":
    main()
