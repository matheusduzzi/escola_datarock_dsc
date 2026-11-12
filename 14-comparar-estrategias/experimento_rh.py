"""O exercício da aula «Comparar estratégias»: as estratégias no acompanhamento do RH.

    python3 experimento_rh.py               # a tabela, depois que você escrever avaliar() e conferir()
    python3 experimento_rh.py --registrar   # o mesmo, e grava o registro em experimento_rh.json
    python3 experimento_rh.py --refazer     # roda de novo e compara com experimento_rh.json
    python3 testar_experimento_rh.py        # os testes das suas duas funções

A parte pronta separa as admissões como na aula 09 (treino até 2025-06-30, validação de julho a
setembro de 2025), ajusta o pipeline da aula 09 no treino e entrega tudo já preparado. O teste
fica fechado. As estratégias são as do estrategias.py da aula. Os preços e as vagas são os do
briefing da Marta, na aula 01.

Você escreve duas funções: avaliar(), que mede uma estratégia com um sorteio, e conferir(), que
compara dois registros do experimento.
"""
import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ACOMPANHAMENTO = 240      # R$ de um acompanhamento, para quem ia ficar ou para quem ia sair
SAIDA = 3000              # R$ de uma saída antes de 180 dias
EFEITO = 0.25             # o acompanhamento evita 1 de cada 4 saídas de quem ia sair
VAGAS_MES = 12            # o RH acompanha no máximo 12 pessoas por mês
EMPATE = ACOMPANHAMENTO / (EFEITO * SAIDA)    # 0,32
SORTEIO = 14
SORTEIOS = list(range(20))
BASE = Path("../dados/pessoas/admissoes.csv")
REGISTRO = Path("experimento_rh.json")


def carregar():
    """Pronto. Retorna o treino e a validação preparados, o mês de cada pessoa da validação e o SHA-256 da base."""
    if not Path("pipeline_pessoas.py").is_file() or not BASE.is_file():
        sys.exit("não achei os arquivos. Rode de dentro da pasta 14-comparar-estrategias do kit.")
    import pipeline_pessoas as pp
    treino, validacao, _, _ = pp.separar(pp.carregar(BASE))
    params = pp.ajustar(treino)
    x_tr = pp.aplicar(params, treino)[params["colunas"]]
    x_va = pp.aplicar(params, validacao)[params["colunas"]]
    t = treino.set_index("id_pessoa").loc[x_tr.index]
    v = validacao.set_index("id_pessoa").loc[x_va.index]
    return {"x_tr": x_tr, "y_tr": t["saiu_180d"].astype(int), "x_va": x_va, "y_va": v["saiu_180d"].astype(int),
            "mes": v["data_admissao"].dt.strftime("%Y-%m"),
            "sha256": hashlib.sha256(BASE.read_bytes()).hexdigest()}


def avaliar(d, nome, sorteio):
    """Mede uma estratégia com um sorteio.

    d: o dicionário de carregar() (ou um igual, com x_tr, y_tr, x_va, y_va e mes).
    nome: uma chave de estrategias.ESTRATEGIAS. sorteio: um inteiro.

    A estratégia mexe só no treino. A validação fica como chegou. A nota de cada pessoa da
    validação é corrigida para a proporção de saídas do treino original, e a regra acompanha quem
    tem a nota corrigida acima do EMPATE.

    Retorna um dicionário com:
      n, saidas   pessoas e saídas da validação em que a estratégia foi medida
      marcadas    quantas pessoas a regra acompanha
      maior_mes   quantas ela acompanha no mês em que acompanha mais
      vp          acompanhou e ia sair
      precisao    vp / marcadas; None quando a regra não marca ninguém
      saldo       em reais, contra não acompanhar ninguém, com o efeito de 1 em 4
      acerto_par  o acerto do par da nota na validação (a correção não muda a ordem)
    """
    raise NotImplementedError("escreva a avaliar(): veja o docstring e as dicas do exercício")


def conferir(antigo, novo):
    """Compara dois registros do experimento (dicionários como os de registro()).

    Retorna (erros, avisos), duas listas de textos curtos, uma linha por diferença:
      erros   qualquer diferença em "dados", "parametros" ou "resultados", inclusive uma chave
              que existe num registro e falta no outro
      avisos  diferenças em "versoes" (Python, pandas, NumPy): elas não impedem de refazer,
              mas precisam aparecer
    Registros iguais retornam ([], []).
    """
    raise NotImplementedError("escreva a conferir(): veja o docstring e as dicas do exercício")


# ---------------------------------------------------------------- pronto daqui para baixo

def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def registro(d, sorteio):
    import estrategias as e
    um = {nome: avaliar(d, nome, sorteio) for nome in e.ESTRATEGIAS}
    varios = {nome: [avaliar(d, nome, s) for s in SORTEIOS] for nome in e.SORTEIAM}
    reg = {
        "dados": {"arquivo": str(BASE), "sha256": d["sha256"]},
        "parametros": {"treino": "até 2025-06-30", "validacao": "2025-07-01 a 2025-09-30", "teste": "fechado",
                       "acompanhamento": ACOMPANHAMENTO, "saida": SAIDA, "efeito": EFEITO, "vagas_mes": VAGAS_MES,
                       "corte": "empate, 0,32, na nota corrigida para a proporção do treino",
                       "sorteio": sorteio, "sorteios": SORTEIOS, "estrategias": list(e.ESTRATEGIAS)},
        "versoes": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "resultados": {
            "um_sorteio": {k: {c: (round(v, 4) if isinstance(v, float) else v) for c, v in r.items()}
                           for k, r in um.items()},
            "vinte_sorteios": {k: [r["saldo"] for r in rs] for k, rs in varios.items()},
        },
    }
    return um, varios, reg


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sorteio", type=int, default=SORTEIO)
    ap.add_argument("--registrar", action="store_true", help="grava o registro em experimento_rh.json")
    ap.add_argument("--refazer", action="store_true", help="compara a rodada com experimento_rh.json")
    args = ap.parse_args()
    d = carregar()
    y_tr, y_va = d["y_tr"], d["y_va"]
    print(f"treino: {len(y_tr)} pessoas admitidas até 30/06/2025, {int(y_tr.sum())} saíram antes de 180 dias "
          f"({pct(y_tr.mean())})")
    print(f"validação: {len(y_va)} pessoas admitidas de julho a setembro de 2025, {int(y_va.sum())} saíram "
          f"({pct(y_va.mean())}), do jeito que chegaram; o teste fica fechado")
    print(f"preços: acompanhamento R$ {ACOMPANHAMENTO}, saída R$ {num(SAIDA, 0)}, evita 1 de cada 4; empate "
          f"{pct(EMPATE)}; vagas: {VAGAS_MES} por mês; sorteio: {args.sorteio}")
    um, varios, reg = registro(d, args.sorteio)
    if args.refazer:
        if not REGISTRO.is_file():
            sys.exit("não achei experimento_rh.json. Rode antes python3 experimento_rh.py --registrar.")
        erros, avisos = conferir(json.loads(REGISTRO.read_text(encoding="utf-8")), reg)
        for a in avisos:
            print(f"aviso, versão diferente: {a}")
        if erros:
            print(f"{len(erros)} diferenças com o registro:")
            for x in erros[:8]:
                print(f"  {x}")
            sys.exit(1)
        print("igual ao registro: os mesmos dados, os mesmos parâmetros e os mesmos resultados")
        return
    print(f"\n1. as cinco estratégias com o sorteio {args.sorteio}, nota corrigida")
    print(f"{'estratégia':<16} {'pessoas':>7} {'marcadas':>8} {'maior mês':>9} {'VP':>4} {'precisão':>9} "
          f"{'saldo':>11} {'acerto do par':>14}")
    for nome, r in um.items():
        print(f"{nome:<16} {r['n']:>7} {r['marcadas']:>8} {r['maior_mes']:>9} {r['vp']:>4} {pct(r['precisao']):>9} "
              f"{reais(r['saldo']):>11} {pct(r['acerto_par']):>14}")
    print(f"\n2. as estratégias que sorteiam, em {len(SORTEIOS)} sorteios, saldo")
    print(f"{'estratégia':<16} {'pior':>11} {'mediana':>11} {'melhor':>11} {'melhor sorteio':>15}")
    for nome, rs in varios.items():
        s = [r["saldo"] for r in rs]
        print(f"{nome:<16} {reais(min(s)):>11} {reais(float(np.median(s))):>11} {reais(max(s)):>11} "
              f"{SORTEIOS[int(np.argmax(s))]:>15}")
    if args.registrar:
        REGISTRO.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"\nregistro gravado em {REGISTRO}")


if __name__ == "__main__":
    main()
