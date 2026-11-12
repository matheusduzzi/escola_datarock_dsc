"""O experimento da aula «Comparar estratégias» do curso ML: preparação e validação.

    python3 comparar.py                          # as cinco estratégias, sorteio 14, e os 20 sorteios
    python3 comparar.py --registrar              # o mesmo, e grava o registro em experimento.json
    python3 comparar.py --refazer                # roda de novo e compara com experimento.json
    python3 comparar.py --sorteio 7 --refazer    # outro sorteio contra o registro: aponta a diferença
    python3 comparar.py --validacao-reamostrada  # o que acontece quando a validação também é reamostrada

As estratégias mexem só nos 1155 pedidos do treino (janeiro a março de 2026). Todas são medidas
nos mesmos 795 pedidos da validação (abril e maio), do jeito que chegaram. Junho, o teste, sai
na leitura e não entra em nenhuma conta. A preparação e o classificador são os da aula 10; os
preços, o empate e o teto são os do briefing da aula 01.
"""
import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("../dados/loja/pedidos_export_completo.csv")
REGISTRO = Path("experimento.json")
LIGACAO = 5           # R$ de uma ligação, acerte ou não
CANCELAMENTO = 15     # R$ de um cancelamento que passa sem ligação
TETO = 0.25           # no máximo 1 ligação para cada 4 pedidos
EMPATE = LIGACAO / CANCELAMENTO
SORTEIO = 14
SORTEIOS = list(range(20))


def carregar():
    if not BASE.is_file() or not Path("estrategias.py").is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 14-comparar-estrategias do kit.")
    import pipeline_corrigido
    base = pd.read_csv(BASE, parse_dates=["data_pedido"])
    x_tr, y_tr, x_va, y_va = pipeline_corrigido.preparar(base)
    return {"x_tr": x_tr, "y_tr": y_tr, "x_va": x_va, "y_va": y_va,
            "sha256": hashlib.sha256(BASE.read_bytes()).hexdigest()}


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def lista(y, nota):
    """As contas de ligar quando a nota passa do empate."""
    y = np.asarray(y).astype(int)
    ligar = np.asarray(nota) > EMPATE
    vp = int((ligar & (y == 1)).sum())
    lig = int(ligar.sum())
    fn = int((~ligar & (y == 1)).sum())
    return {"ligacoes": lig, "vp": vp, "precisao": vp / lig if lig else None,
            "revocacao": vp / (vp + fn), "custo": LIGACAO * lig + CANCELAMENTO * fn,
            "cabe": lig <= len(y) * TETO}


def rodar(nome, sorteio, d):
    """Uma estratégia com um sorteio: mexe no treino, treina e mede na validação intocada."""
    import classificador
    import estrategias as e
    n_va = len(d["y_va"])
    x, y, pesos = e.ESTRATEGIAS[nome](d["x_tr"], d["y_tr"], sorteio)
    modelo = e.treinar(x, y, pesos)
    nota = classificador.nota(modelo, d["x_va"])
    if len(nota) != n_va:
        raise RuntimeError("a validação mudou de tamanho")
    vista = e.proporcao(y, pesos)
    corrigida = e.corrigir_nota(nota, vista, e.proporcao(d["y_tr"]))
    yv = d["y_va"].to_numpy()
    return {"linhas": len(y), "vista": vista, "acerto_par": classificador.acerto_do_par(nota, yv),
            "nota_media": float(nota.mean()), "corrigida_media": float(corrigida.mean()),
            "bruta": lista(yv, nota), "corrigida": lista(yv, corrigida)}


def para_registro(r):
    """Os números como a tabela mostra: inteiros e porcentagens com uma casa."""
    def p(x):
        return None if x is None else round(100 * x, 1)
    return {"linhas": r["linhas"], "cancelados_vistos": p(r["vista"]), "acerto_par": p(r["acerto_par"]),
            "nota_media": p(r["nota_media"]),
            "nota_como_sai": {"ligacoes": r["bruta"]["ligacoes"], "custo": r["bruta"]["custo"]},
            "nota_corrigida": {"ligacoes": r["corrigida"]["ligacoes"], "vp": r["corrigida"]["vp"],
                               "precisao": p(r["corrigida"]["precisao"]), "revocacao": p(r["corrigida"]["revocacao"]),
                               "custo": r["corrigida"]["custo"]}}


def experimento(d, sorteio):
    import estrategias as e
    um = {nome: rodar(nome, sorteio, d) for nome in e.ESTRATEGIAS}
    varios = {nome: [rodar(nome, s, d) for s in SORTEIOS] for nome in e.SORTEIAM}
    registro = {
        "dados": {"arquivo": str(BASE), "sha256": d["sha256"]},
        "parametros": {"treino": "2026-01-01 a 2026-03-31", "validacao": "2026-04-01 a 2026-05-31",
                       "teste": "junho de 2026, fora", "ligacao": LIGACAO, "cancelamento": CANCELAMENTO,
                       "corte": "empate, 5/15, na nota corrigida para a proporção do treino",
                       "teto": TETO, "vizinhos_smote": e.VIZINHOS, "sorteio": sorteio, "sorteios": SORTEIOS,
                       "estrategias": list(e.ESTRATEGIAS)},
        "versoes": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "resultados": {
            "um_sorteio": {nome: para_registro(r) for nome, r in um.items()},
            "vinte_sorteios": {nome: {"custo": [r["corrigida"]["custo"] for r in rs],
                                      "acerto_par": [round(100 * r["acerto_par"], 1) for r in rs]}
                               for nome, rs in varios.items()},
        },
    }
    return um, varios, registro


def diferencas(antigo, novo, caminho=""):
    """Onde dois registros diferem. Retorna (erros, avisos): versão diferente é aviso, o resto é erro."""
    erros, avisos = [], []
    for chave in sorted(set(antigo) | set(novo)):
        onde = f"{caminho}{chave}"
        if chave not in novo or chave not in antigo:
            erros.append(f"{onde}: só existe {'no registro' if chave in antigo else 'na rodada nova'}")
            continue
        a, b = antigo[chave], novo[chave]
        if isinstance(a, dict) and isinstance(b, dict):
            e2, a2 = diferencas(a, b, onde + ".")
            erros += e2
            avisos += a2
        elif a != b:
            (avisos if onde.startswith("versoes.") else erros).append(f"{onde}: registro {a}, agora {b}")
    return erros, avisos


def imprimir(d, um, varios, sorteio):
    import estrategias as e
    y_tr, y_va = d["y_tr"], d["y_va"]
    n_va = len(y_va)
    print(f"treino: {len(y_tr)} pedidos de janeiro a março de 2026, {int(y_tr.sum())} cancelados ({pct(y_tr.mean())})")
    print(f"validação: {n_va} pedidos de abril e maio de 2026, {int(y_va.sum())} cancelados ({pct(y_va.mean())}), "
          "do jeito que chegaram; junho, o teste, fica fora")
    print(f"preços: ligação R$ {LIGACAO}, cancelamento sem ligação R$ {CANCELAMENTO}; liga quando a nota passa de "
          f"{num(EMPATE, 3)}; teto: {int(n_va * TETO)} ligações")
    print(f"sorteio: {sorteio}; dados: {d['sha256'][:12]}")

    print("\n1. o que cada estratégia muda no treino, e o que isso faz com a nota")
    print(f"{'estratégia':<16} {'linhas':>6} {'cancelados':>10} {'acerto do par':>14} {'nota média':>11}")
    for nome, r in um.items():
        print(f"{nome:<16} {r['linhas']:>6} {pct(r['vista']):>10} {pct(r['acerto_par']):>14} {pct(r['nota_media']):>11}")
    print(f"   na validação, {pct(y_va.mean())} dos pedidos cancelaram; no peso de classe, os cancelados contam "
          "como metade do treino")

    print("\n2. ligar quando a nota passa do empate, com a nota como sai")
    print(f"{'estratégia':<16} {'ligações':>8} {'custo':>9} {'cabe?':>6}")
    for nome, r in um.items():
        b = r["bruta"]
        print(f"{nome:<16} {b['ligacoes']:>8} {reais(b['custo']):>9} {'sim' if b['cabe'] else 'não':>6}")

    print(f"\n3. a mesma regra com a nota corrigida para os {pct(y_tr.mean())} de cancelados do treino")
    print(f"{'estratégia':<16} {'ligações':>8} {'precisão':>9} {'revocação':>10} {'custo':>9} {'cabe?':>6} "
          f"{'nota média':>11}")
    for nome, r in um.items():
        c = r["corrigida"]
        print(f"{nome:<16} {c['ligacoes']:>8} {pct(c['precisao']):>9} {pct(c['revocacao']):>10} "
              f"{reais(c['custo']):>9} {'sim' if c['cabe'] else 'não':>6} {pct(r['corrigida_media']):>11}")

    print(f"\n4. as estratégias que sorteiam, em {len(SORTEIOS)} sorteios ({SORTEIOS[0]} a {SORTEIOS[-1]}), "
          "nota corrigida")
    print(f"{'estratégia':<16} {'acerto do par':>15} {'custo menor':>12} {'mediana':>9} {'maior':>9}")
    for nome, rs in varios.items():
        a = [r["acerto_par"] for r in rs]
        c = [r["corrigida"]["custo"] for r in rs]
        faixa = f"{num(100 * min(a))} a {num(100 * max(a))}%"
        print(f"{nome:<16} {faixa:>15} {reais(min(c)):>12} {reais(float(np.median(c))):>9} {reais(max(c)):>9}")
    fixas = [n for n in e.ESTRATEGIAS if n not in e.SORTEIAM]
    print("   " + " e ".join(fixas) + " não sorteiam nada: " +
          " e ".join(reais(um[n]["corrigida"]["custo"]) for n in fixas) + " em qualquer sorteio")


def reamostrada(d, sorteio):
    """A armadilha: a validação reamostrada para metade de cada classe, como o treino."""
    import classificador
    import estrategias as e
    yv = d["y_va"].to_numpy()
    x, y, pesos = e.subamostragem(d["x_tr"], d["y_tr"], sorteio)
    modelo = e.treinar(x, y, pesos)
    nota = classificador.nota(modelo, d["x_va"]).to_numpy()
    xv, yv2, _ = e.subamostragem(d["x_va"], d["y_va"], sorteio)      # o erro: reamostrar a validação
    nota2 = classificador.nota(modelo, xv).to_numpy()
    print(f"subamostragem no treino, sorteio {sorteio}, nota como sai, liga quando passa de {num(EMPATE, 3)}")
    print(f"{'medida em':<34} {'pedidos':>7} {'cancelados':>10} {'ligações':>8} {'precisão':>9} {'revocação':>10} "
          f"{'custo':>9} {'nunca liga':>10} {'economia':>9}")
    for rotulo, yy, nn in [("validação reamostrada, 50% e 50%", yv2.to_numpy(), nota2),
                           ("validação como chegou", yv, nota)]:
        r = lista(yy, nn)
        nunca = CANCELAMENTO * int(yy.sum())
        print(f"{rotulo:<34} {len(yy):>7} {pct(yy.mean()):>10} {r['ligacoes']:>8} {pct(r['precisao']):>9} "
              f"{pct(r['revocacao']):>10} {reais(r['custo']):>9} {reais(nunca):>10} {reais(nunca - r['custo']):>9}")
    print("   economia: contra não ligar para ninguém, nos mesmos pedidos")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sorteio", type=int, default=SORTEIO, help="o número do sorteio das estratégias")
    ap.add_argument("--registrar", action="store_true", help="grava o registro em experimento.json")
    ap.add_argument("--refazer", action="store_true", help="compara a rodada com experimento.json")
    ap.add_argument("--validacao-reamostrada", action="store_true", help="a armadilha de reamostrar a validação")
    args = ap.parse_args()
    d = carregar()
    if args.validacao_reamostrada:
        reamostrada(d, args.sorteio)
        return
    um, varios, registro = experimento(d, args.sorteio)
    if args.refazer:
        if not REGISTRO.is_file():
            sys.exit("não achei experimento.json. Rode antes python3 comparar.py --registrar.")
        antigo = json.loads(REGISTRO.read_text(encoding="utf-8"))
        erros, avisos = diferencas(antigo, registro)
        print(f"refiz o experimento e comparei com {REGISTRO}")
        for a in avisos:
            print(f"aviso, versão diferente: {a}")
        if erros:
            print(f"{len(erros)} diferenças:")
            for x in erros[:8]:
                print(f"  {x}")
            if len(erros) > 8:
                print(f"  e mais {len(erros) - 8}")
            sys.exit(1)
        n = sum(1 for _ in _folhas(registro["resultados"]))
        print(f"igual ao registro: os mesmos dados, os mesmos parâmetros e os {n} números dos resultados")
        return
    imprimir(d, um, varios, args.sorteio)
    if args.registrar:
        REGISTRO.write_text(json.dumps(registro, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"\nregistro gravado em {REGISTRO}")


def _folhas(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _folhas(v)
    elif isinstance(x, list):
        for v in x:
            yield from _folhas(v)
    else:
        yield x


if __name__ == "__main__":
    main()
