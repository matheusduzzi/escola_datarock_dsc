"""O modelo da consultoria com outros sorteios do teste: random_state de 1 a 20.

Aula «Auditoria de um pipeline» do curso ML: preparação e validação. Rode de dentro da pasta da aula:

    python3 sorteios.py

Nada mais muda: o mesmo preparar() deles, o mesmo classificador e o mesmo corte. Só o sorteio
dos 30% do teste. O 17 é o que a consultoria usou. O programa troca o random_state que o
preparar() deles passa ao sample() do pandas, sem mexer no arquivo deles.
"""
import sys
from pathlib import Path

import pandas as pd

if not Path("consultoria_cancelamento.py").is_file():
    sys.exit("não achei os arquivos. Rode de dentro da pasta 17-auditoria-de-um-pipeline do kit.")

import consultoria_cancelamento as consultoria  # noqa: E402
from auditoria import medir, pct  # noqa: E402
from classificador import nota, treinar  # noqa: E402


def main():
    base = pd.read_csv(consultoria.BASE, parse_dates=["data_pedido"])
    original = pd.DataFrame.sample
    linhas = []
    for estado in range(1, 21):
        def sample(self, *args, _estado=estado, **kwargs):
            kwargs["random_state"] = _estado
            return original(self, *args, **kwargs)
        pd.DataFrame.sample = sample
        try:
            x_tr, y_tr, x_te, y_te = consultoria.preparar(base)
        finally:
            pd.DataFrame.sample = original
        m = medir(y_te, nota(treinar(x_tr, y_tr), x_te), consultoria.CORTE)
        linhas.append((estado, m))
    print(f"{'sorteio':>8}{'precisão':>10}{'revocação':>11}")
    for estado, m in linhas:
        print(f"{estado:>8}{pct(m['precisao']):>10}{pct(m['revocacao']):>11}" + ("   o da consultoria" if estado == 17 else ""))
    p = sorted(m["precisao"] for _, m in linhas)
    r = sorted(m["revocacao"] for _, m in linhas)
    acima = sum(m["precisao"] >= linhas[16][1]["precisao"] for _, m in linhas)
    print(f"\nprecisão de {pct(p[0])} a {pct(p[-1])}; revocação de {pct(r[0])} a {pct(r[-1])}")
    print(f"sorteios com precisão igual ou maior que a do 17: {acima} de {len(linhas)}")


if __name__ == "__main__":
    main()
