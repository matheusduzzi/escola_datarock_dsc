"""Monta o rótulo "saiu até H dias depois da admissão" a partir das datas e mostra quem tem resposta.

Rode de dentro da pasta da aula:

    python3 rotulo.py                  # horizonte de 180 dias, lista no dia 7
    python3 rotulo.py --horizonte 90
    python3 rotulo.py --decisao 14

Lê ../dados/pessoas/admissoes.csv. A base foi extraída em 2026-06-30.
Uma pessoa tem resposta quando já saiu até H dias depois da admissão (rótulo 1)
ou quando já completou H dias na data da extração sem sair (rótulo 0).
"""
import argparse
import sys

import pandas as pd

ARQUIVO = "../dados/pessoas/admissoes.csv"
EXTRACAO = pd.Timestamp("2026-06-30")


def inteiro_positivo(texto):
    try:
        valor = int(texto)
    except ValueError:
        raise argparse.ArgumentTypeError(f"precisa ser um número inteiro de dias, veio {texto}")
    if valor <= 0:
        raise argparse.ArgumentTypeError(f"precisa ser maior que zero, veio {valor}")
    return valor


def pct(parte, total):
    return f"{100 * parte / total:.1f}%".replace(".", ",")


def montar_rotulo(adm, horizonte):
    """1 se saiu até `horizonte` dias; 0 se completou `horizonte` dias sem sair; vazio se ainda não dá para saber."""
    dias = (adm["data_desligamento"] - adm["data_admissao"]).dt.days
    saiu = dias.le(horizonte)  # vazio (ainda na empresa) vira False
    completou = adm["data_admissao"] + pd.Timedelta(days=horizonte) <= EXTRACAO
    rotulo = pd.Series(pd.NA, index=adm.index, dtype="Int64")
    rotulo[completou & ~saiu] = 0
    rotulo[saiu] = 1
    return rotulo, dias, completou


def main():
    parser = argparse.ArgumentParser(description="Rótulo de saída antes do horizonte, nas admissões da Loja Exemplo.")
    parser.add_argument("--horizonte", type=inteiro_positivo, default=180,
                        help="dias depois da admissão em que a saída conta (padrão 180)")
    parser.add_argument("--decisao", type=inteiro_positivo, default=7,
                        help="dia, depois da admissão, em que a lista do RH sai (padrão 7)")
    args = parser.parse_args()
    if args.decisao >= args.horizonte:
        parser.error(f"a lista precisa sair antes do fim do horizonte: dia {args.decisao} "
                     f"não é antes de {args.horizonte}")

    adm = pd.read_csv(ARQUIVO, parse_dates=["data_admissao", "data_desligamento"])
    h = args.horizonte
    rotulo, dias, completou = montar_rotulo(adm, h)
    limite = (EXTRACAO - pd.Timedelta(days=h)).date()

    print(f"admissões: {len(adm)}, de {adm['data_admissao'].min().date()} a {adm['data_admissao'].max().date()}; "
          f"base extraída em {EXTRACAO.date()}")
    print(f"rótulo: saiu até {h} dias depois da admissão; a lista sai no dia {args.decisao}")
    print(f"quem completou {h} dias: quem entrou até {limite}")
    if h == 180:
        coluna = adm["saiu_180d"].astype("Int64")
        iguais = int(((coluna == rotulo) | (coluna.isna() & rotulo.isna())).fillna(False).sum())
        print(f"rótulo refeito pelas datas igual à coluna saiu_180d: {iguais} de {len(adm)}")
    else:
        print("a coluna saiu_180d vale só para 180 dias; aqui o rótulo sai só das datas")
    print()

    tri = adm["data_admissao"].dt.year.astype(str) + "-T" + adm["data_admissao"].dt.quarter.astype(str)
    print(f"{'trimestre':<10}{'admissões':>10}{'com resposta':>14}{'saíram':>8}{'% saíram':>10}")
    for t in sorted(tri.unique()):
        m = tri == t
        com, sai = int(rotulo[m].notna().sum()), int((rotulo[m] == 1).sum())
        print(f"{t:<10}{int(m.sum()):>10}{com:>14}{sai:>8}{pct(sai, com) if com else '-':>10}")
    print()

    presente = ~dias.le(args.decisao)
    contas = [
        ("todas as linhas", pd.Series(True, index=adm.index)),
        ("só quem tem resposta", rotulo.notna()),
        (f"só quem completou {h} dias", completou),
        (f"e ainda estava lá no dia {args.decisao}", completou & presente),
    ]
    print(f"{'conta':<36}{'pessoas':>8}{'saíram':>8}{'% saíram':>10}")
    for nome, m in contas:
        n, sai = int(m.sum()), int((rotulo[m] == 1).sum())
        print(f"{nome:<36}{n:>8}{sai:>8}{pct(sai, n):>10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
