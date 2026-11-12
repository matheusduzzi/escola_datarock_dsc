"""Gera a base de admissões da Loja Exemplo usada no caso de pessoas do curso.

Só biblioteca padrão (Python 3.9 ou mais novo). Semente fixa: rodar duas vezes dá o mesmo
arquivo, byte a byte.

    python3 gerar.py                 # escreve admissoes.csv nesta pasta
    python3 gerar.py --saida /tmp/x  # escreve em outra pasta

Uma linha é uma pessoa contratada entre 2024-07-01 e 2026-05-31. A base foi extraída em
2026-06-30 (DATA_CORTE). O RH quer oferecer acompanhamento no primeiro mês para quem tem mais
chance de sair antes de 180 dias. O modelo não entra na decisão de contratar.

Nas aulas, você prepara e avalia primeiro e só depois lê este programa para comparar.
"""
import argparse
import csv
import datetime
import math
import pathlib
import random

SEMENTE = 2024
N = 1500
INICIO = datetime.date(2024, 7, 1)
FIM = datetime.date(2026, 5, 31)
DATA_CORTE = datetime.date(2026, 6, 30)
HORIZONTE = 180
INICIO_DISTANCIA = datetime.date(2025, 3, 1)
INICIO_DIGITAL = datetime.date(2025, 10, 1)
INICIO_L08 = datetime.date(2026, 1, 1)

LOJAS = [("L01", 18, 0.0), ("L02", 16, 0.15), ("L03", 14, -0.1), ("L04", 14, 0.3),
         ("L05", 12, -0.2), ("L06", 12, 0.1), ("L07", 10, 0.0)]
CARGOS = [("caixa", 30, (1900, 2300), 0.0), ("estoque", 26, (1950, 2450), 0.35),
          ("atendimento", 24, (2000, 2600), -0.15), ("entregador", 20, (2100, 2800), 0.55)]
DIGITAL = ("atendimento digital", (2300, 3000), -0.3)
TURNOS = [("manha", 45, 0.0), ("tarde", 35, 0.1), ("noite", 20, 0.5)]
DIGITACAO = 4


def _sorteio(rng, opcoes):
    return rng.choices(opcoes, weights=[o[1] for o in opcoes])[0]


def gerar(saida):
    rng = random.Random(SEMENTE)
    saida.mkdir(parents=True, exist_ok=True)
    dias = (FIM - INICIO).days
    linhas = []
    for i in range(1, N + 1):
        adm = INICIO + datetime.timedelta(days=rng.randint(0, dias))
        if adm >= INICIO_L08 and rng.random() < 0.12:
            loja, efeito_loja = "L08", 0.45
        else:
            loja, _, efeito_loja = _sorteio(rng, LOJAS)
        if adm >= INICIO_DIGITAL and rng.random() < 0.18:
            cargo, (lo, hi), efeito_cargo = DIGITAL
        else:
            cargo, _, (lo, hi), efeito_cargo = _sorteio(rng, CARGOS)
        turno, _, efeito_turno = _sorteio(rng, TURNOS)
        salario = round(rng.uniform(lo, hi) / 10) * 10
        distancia = round(min(rng.expovariate(1 / 7.0) + 0.5, 45.0), 1)
        indicacao = 1 if rng.random() < 0.28 else 0

        logito = (-1.55 + efeito_cargo + efeito_turno + efeito_loja
                  + 0.045 * (distancia - 7) - 0.65 * indicacao
                  - 0.0009 * (salario - 2300) + rng.gauss(0, 0.5))
        sai_cedo = rng.random() < 1 / (1 + math.exp(-logito))
        if sai_cedo:
            dias_ate_sair = rng.randint(5, HORIZONTE)
        elif rng.random() < 0.3:
            dias_ate_sair = rng.randint(HORIZONTE + 1, 600)
        else:
            dias_ate_sair = None
        saida_data = adm + datetime.timedelta(days=dias_ate_sair) if dias_ate_sair else None
        if saida_data and saida_data > DATA_CORTE:
            saida_data = None  # ainda empregada na extração

        if saida_data and (saida_data - adm).days < 30:
            horas = round((saida_data - adm).days * rng.uniform(0.3, 0.8))
        else:
            horas = rng.randint(16, 40)

        maduro = adm + datetime.timedelta(days=HORIZONTE) <= DATA_CORTE
        if saida_data and (saida_data - adm).days <= HORIZONTE:
            rotulo = "1"
        elif maduro:
            rotulo = "0"
        else:
            rotulo = ""

        sem_distancia = (adm < INICIO_DISTANCIA and rng.random() < 0.7) or rng.random() < 0.03
        linhas.append({
            "id_pessoa": i, "data_admissao": adm.isoformat(), "loja": loja, "cargo": cargo,
            "turno": turno, "salario_base": salario,
            "distancia_km": "" if sem_distancia else "%.1f" % distancia,
            "indicacao": indicacao, "horas_treinamento": horas,
            "data_desligamento": saida_data.isoformat() if saida_data else "",
            "saiu_180d": rotulo,
        })

    for linha in rng.sample(linhas, DIGITACAO):
        linha["salario_base"] = linha["salario_base"] * 10

    linhas.sort(key=lambda l: (l["data_admissao"], l["id_pessoa"]))
    colunas = list(linhas[0])
    with open(saida / "admissoes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)

    com_rotulo = [l for l in linhas if l["saiu_180d"] != ""]
    return {
        "pessoas": len(linhas),
        "com_rotulo": len(com_rotulo),
        "saiu_180d": sum(1 for l in com_rotulo if l["saiu_180d"] == "1"),
        "sem_rotulo": len(linhas) - len(com_rotulo),
        "distancia_vazia": sum(1 for l in linhas if l["distancia_km"] == ""),
        "atendimento_digital": sum(1 for l in linhas if l["cargo"] == DIGITAL[0]),
        "loja_L08": sum(1 for l in linhas if l["loja"] == "L08"),
    }


def main():
    parser = argparse.ArgumentParser(description="Gera admissoes.csv da Loja Exemplo.")
    parser.add_argument("--saida", default=str(pathlib.Path(__file__).resolve().parent))
    args = parser.parse_args()
    resumo = gerar(pathlib.Path(args.saida))
    print(" ".join("%s=%s" % (k, v) for k, v in resumo.items()))


if __name__ == "__main__":
    main()
