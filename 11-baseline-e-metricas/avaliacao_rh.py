"""O exercício da aula «Baseline e métricas»: a tabela de avaliação do acompanhamento do RH.

    python3 avaliacao_rh.py           # a tabela, depois que você escrever linha() e regras()
    python3 testar_avaliacao_rh.py    # os testes da sua linha() e das suas regras()

A parte pronta separa as admissões como na aula 09 (treino até 2025-06-30, validação de julho a
setembro de 2025), ajusta o pipeline da aula 09 no treino, treina o classificador da aula 10 e dá
a nota de cada pessoa da validação. O teste fica fechado.

Você escreve duas funções: linha(), que faz a conta de uma regra, e regras(), que monta as quatro
regras a comparar. Os preços e as vagas são os do briefing da Marta, na aula 01.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ACOMPANHAMENTO = 240      # R$ de um acompanhamento, para quem ia ficar ou para quem ia sair
SAIDA = 3000              # R$ de uma saída antes de 180 dias
EFEITO = 0.25             # o acompanhamento evita 1 de cada 4 saídas de quem ia sair
VAGAS_MES = 12            # o RH acompanha no máximo 12 pessoas por mês
EMPATE = ACOMPANHAMENTO / (EFEITO * SAIDA)    # 0,32: a precisão mínima para o acompanhamento se pagar


def carregar():
    """Pronto. Retorna uma tabela da validação: mes, turno, saiu_180d e nota, uma linha por pessoa."""
    if not Path("pipeline_pessoas.py").is_file() or not Path("../dados/pessoas/admissoes.csv").is_file():
        sys.exit("não achei os arquivos. Rode de dentro da pasta 11-baseline-e-metricas do kit.")
    import classificador
    import pipeline_pessoas as pp
    treino, validacao, _, _ = pp.separar(pp.carregar())
    params = pp.ajustar(treino)
    x_tr = pp.aplicar(params, treino)
    x_va = pp.aplicar(params, validacao)
    y_tr = treino.set_index("id_pessoa").loc[x_tr.index, "saiu_180d"]
    modelo = classificador.treinar(x_tr[params["colunas"]], y_tr)
    v = validacao.set_index("id_pessoa").loc[x_va.index]
    return pd.DataFrame({"mes": v["data_admissao"].dt.strftime("%Y-%m"), "turno": v["turno"],
                         "saiu_180d": v["saiu_180d"].astype(int),
                         "nota": classificador.nota(modelo, x_va[params["colunas"]])})


def linha(y, marcar, mes):
    """A conta de uma regra.

    y: 1 para quem saiu antes de 180 dias, 0 para quem ficou.
    marcar: True para quem a regra manda acompanhar.
    mes: o mês de admissão de cada pessoa, no formato "2025-07".
    Os três têm o mesmo tamanho e a mesma ordem; tamanhos diferentes são um erro (ValueError).

    Retorna um dicionário com:
      marcadas    quantas pessoas a regra acompanha
      maior_mes   quantas ela acompanha no mês em que acompanha mais
      vp, fp, fn  acompanhou e ia sair; acompanhou e ia ficar; saiu sem acompanhamento
      precisao    vp / marcadas; None quando a regra não marca ninguém
      revocacao   vp / (vp + fn)
      saldo       em reais, contra não acompanhar ninguém: o que as saídas evitadas economizam
                  menos o que os acompanhamentos custam
    """
    raise NotImplementedError("escreva a linha() da tabela")


def regras(v):
    """As quatro regras, cada uma com um True para quem ela acompanha.

    Retorna um dicionário com as chaves, nesta ordem:
      "ninguém", "todos", "turno da noite", "classificador, nota acima do empate"
    e, em cada uma, uma Series de True/False com o mesmo índice de v.
    """
    raise NotImplementedError("escreva as regras()")


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


def main():
    v = carregar()
    y = v["saiu_180d"]
    print(f"validação: {len(v)} pessoas admitidas de julho a setembro de 2025, {int(y.sum())} saíram antes "
          f"de 180 dias ({pct(y.mean())}); o teste fica fechado")
    print(f"preços: acompanhamento R$ {ACOMPANHAMENTO}, saída R$ {num(SAIDA, 0)}, evita 1 de cada 4; "
          f"empate {pct(EMPATE)}; vagas: {VAGAS_MES} por mês")
    import classificador
    print(f"acerto do par do classificador na validação: {pct(classificador.acerto_do_par(v['nota'], y))}")
    print(f"\n{'regra':<36} {'marcadas':>8} {'maior mês':>9} {'VP':>4} {'FP':>4} {'FN':>4} {'precisão':>9} "
          f"{'revocação':>10} {'saldo':>10} {'cabe?':>6}")
    for nome, marcar in regras(v).items():
        r = linha(y.to_numpy(), np.asarray(marcar, dtype=bool), v["mes"].to_numpy())
        print(f"{nome:<36} {r['marcadas']:>8} {r['maior_mes']:>9} {r['vp']:>4} {r['fp']:>4} {r['fn']:>4} "
              f"{pct(r['precisao']):>9} {pct(r['revocacao']):>10} {reais(r['saldo']):>10} "
              f"{'sim' if r['maior_mes'] <= VAGAS_MES else 'não':>6}")


if __name__ == "__main__":
    main()
