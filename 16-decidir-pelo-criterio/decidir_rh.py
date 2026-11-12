"""O exercício da aula «Decidir pelo critério»: abrir o teste do acompanhamento uma vez e aplicar a régua.

    python3 decidir_rh.py                                         # mostra o plano; o teste continua fechado
    python3 decidir_rh.py --abrir                                 # abre o teste, aplica a régua e anota a abertura
    python3 decidir_rh.py --abrir --regua regua-rh-do-rafael.json   # outro plano depois da abertura

O plano fica em regua_rh.json: preços, efeito, vagas, corte e as quatro condições da Marta.
A parte pronta separa as admissões como na aula 09, ajusta o pipeline no treino (admitidas até
30/06/2025), treina o classificador da aula 10 e, só com --abrir, dá a nota das pessoas do teste.
Você escreve aplicar_regua(). Antes disso, o programa não abre o teste.
"""
import argparse
import json
import sys
from pathlib import Path

from decidir import diferencas, impressao, ler_plano, num, pct, reais

BASE = Path("../dados/pessoas/admissoes.csv")
REGUA = Path("regua_rh.json")
ABERTURA = Path("abertura_rh.json")


def empate(plano):
    p = plano["precos"]
    return p["acompanhamento"] / (p["efeito"] * p["saida"])


def corte_de(plano):
    return empate(plano) if plano["corte"] == "empate" else float(plano["corte"])


def medir(y, marcar, mes, precos):
    """Pronta. As contas de uma regra, como na aula 11: o saldo é contra não acompanhar ninguém."""
    import pandas as pd
    vp = int((marcar & (y == 1)).sum())
    fp = int((marcar & (y == 0)).sum())
    fn = int((~marcar & (y == 1)).sum())
    marcadas = vp + fp
    por_mes = pd.Series(marcar).groupby(mes).sum()
    return {"marcadas": marcadas, "maior_mes": int(por_mes.max()) if marcadas else 0,
            "vp": vp, "fp": fp, "fn": fn,
            "precisao": vp / marcadas if marcadas else None,
            "revocacao": vp / (vp + fn) if vp + fn else None,
            "saldo": vp * precos["efeito"] * precos["saida"] - marcadas * precos["acompanhamento"]}


def aplicar_regua(medida, regua):
    """As quatro condições da régua, na ordem, e a decisão.

    medida: o dicionário de medir() (precisao, revocacao, saldo, maior_mes...).
    regua: o bloco "regua" do plano: precisao_minima, revocacao_minima, saldo_maior_que, vagas_mes.

    Retorna (condicoes, decisao).
      condicoes: lista de 4 tuplas (texto, passa), nesta ordem:
        precisão de pelo menos precisao_minima (precisão None não passa);
        revocação de pelo menos revocacao_minima;
        saldo maior que saldo_maior_que (igual não passa);
        no mês mais cheio, no máximo vagas_mes pessoas.
      decisao: "uso" se as quatro passam; senão "não uso".
    """
    raise NotImplementedError("escreva a aplicar_regua(): as quatro condições e a decisão")


def _regra_escrita():
    """True se aplicar_regua() já foi escrita. O teste só abre depois da regra."""
    exemplo = {"precisao": 0.5, "revocacao": 0.5, "saldo": 1, "maior_mes": 1}
    try:
        aplicar_regua(exemplo, {"precisao_minima": 0.4, "revocacao_minima": 0.25, "saldo_maior_que": 0,
                                "vagas_mes": 12})
    except NotImplementedError:
        return False
    return True


def abrir(plano):
    """Pronta. Ajusta no treino e mede ninguém e o classificador nas pessoas do teste."""
    if not BASE.is_file() or not Path("pipeline_pessoas.py").is_file():
        sys.exit(f"não achei {BASE}. Rode de dentro da pasta 16-decidir-pelo-criterio do kit.")
    import hashlib
    import numpy as np
    import classificador
    import pipeline_pessoas as pp
    a = pp.carregar(BASE)
    treino, _, n_teste, _ = pp.separar(a)
    dias = (a["data_desligamento"] - a["data_admissao"]).dt.days
    contrato = (a["data_admissao"] <= pp.FIM_CONTRATO) & ~(dias <= 7)       # o contrato do alvo da aula 03
    teste = a[contrato & (a["data_admissao"] > pp.FIM_VALIDACAO)]
    if len(teste) != n_teste:
        sys.exit(f"o teste tem {len(teste)} pessoas e o pipeline da aula 09 conta {n_teste}")
    params = pp.ajustar(treino)
    x_tr = pp.aplicar(params, treino)
    y_tr = treino.set_index("id_pessoa").loc[x_tr.index, "saiu_180d"]
    modelo = classificador.treinar(x_tr[params["colunas"]], y_tr)
    x_te = pp.aplicar(params, teste)
    t = teste.set_index("id_pessoa").loc[x_te.index]
    nota = classificador.nota(modelo, x_te[params["colunas"]]).to_numpy()
    y = t["saiu_180d"].astype(int).to_numpy()
    mes = t["data_admissao"].dt.strftime("%Y-%m").to_numpy()
    corte = corte_de(plano)
    regras = {"ninguém": np.zeros(len(y), dtype=bool), f"classificador, corte {num(corte, 3)}": nota > corte}
    return {"dados": hashlib.sha256(BASE.read_bytes()).hexdigest(), "treino": len(treino),
            "pessoas": len(y), "saidas": int(y.sum()),
            "regras": {k: medir(y, m, mes, plano["precos"]) for k, m in regras.items()}}


def relatorio(plano, resultado):
    n = resultado["pessoas"]
    print(f"teste: {n} pessoas admitidas de 1º de outubro de 2025 a 1º de janeiro de 2026, "
          f"{resultado['saidas']} saíram antes de 180 dias ({pct(resultado['saidas'] / n)})")
    print(f"classificador ajustado nas {resultado['treino']} pessoas admitidas até 30/06/2025\n")
    print(f"{'regra':<28} {'marcadas':>8} {'maior mês':>9} {'VP':>4} {'FP':>4} {'FN':>4} {'precisão':>9} "
          f"{'revocação':>10} {'saldo':>10}")
    for nome, m in resultado["regras"].items():
        print(f"{nome:<28} {m['marcadas']:>8} {m['maior_mes']:>9} {m['vp']:>4} {m['fp']:>4} {m['fn']:>4} "
              f"{pct(m['precisao']):>9} {pct(m['revocacao']):>10} {reais(m['saldo']):>10}")
    nome = [k for k in resultado["regras"] if k.startswith("classificador")][0]
    condicoes, decisao = aplicar_regua(resultado["regras"][nome], plano["regua"])
    print(f"\na régua de {plano['escrito_em']}, aplicada à lista do {nome}")
    for texto, passa in condicoes:
        print(f"  {texto:<58} {'passa' if passa else 'não passa'}")
    print(f"\ndecisão pela régua: {decisao}")


def main():
    ap = argparse.ArgumentParser(description="Abre o teste do acompanhamento uma vez e aplica a régua da Marta.")
    ap.add_argument("--regua", default=str(REGUA), help="o arquivo do plano (padrão: regua_rh.json)")
    ap.add_argument("--abrir", action="store_true", help="abre o teste e aplica a régua")
    args = ap.parse_args()
    plano = ler_plano(args.regua)
    p = plano["precos"]
    print(f"plano: {args.regua}, escrito em {plano['escrito_em']}, impressão digital {impressao(plano)}")
    print(f"corte: {plano['corte']} ({num(corte_de(plano), 3)}); preços: acompanhamento {reais(p['acompanhamento'])}, "
          f"saída {reais(p['saida'])}, efeito 1 em {round(1 / p['efeito'])}")

    if not args.abrir:
        print("teste: fechado. Nenhuma pessoa do teste foi lida. Para abrir, uma vez: python3 decidir_rh.py --abrir")
        return
    if not _regra_escrita():
        sys.exit("a aplicar_regua() ainda não foi escrita. Escreva a regra e rode os testes antes de abrir o teste.")

    if ABERTURA.is_file():
        anotada = json.loads(ABERTURA.read_text(encoding="utf-8"))
        mudou = diferencas(anotada["plano"], plano)
        if mudou:
            print(f"\nrecusado: o teste já foi aberto com o plano {impressao(anotada['plano'])}, e esse é outro.",
                  file=sys.stderr)
            for linha in mudou:
                print(f"  {linha}", file=sys.stderr)
            print("um plano novo pede um teste que ainda não foi aberto. O resultado continua o anotado.",
                  file=sys.stderr)
            sys.exit(1)
        resultado = abrir(plano)
        if resultado != anotada["resultado"]:
            print("\nrecusado: com o mesmo plano, a conta de agora não bate com a anotada. "
                  "As pessoas ou o código mudaram depois da abertura.", file=sys.stderr)
            sys.exit(1)
        print(f"\no teste já foi aberto com esse plano. A conta de agora é igual à anotada em {ABERTURA}.")
        relatorio(plano, resultado)
        return

    resultado = abrir(plano)
    ABERTURA.write_text(json.dumps({"plano": plano, "resultado": resultado}, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"\nteste aberto agora. Plano e resultado anotados em {ABERTURA}.")
    relatorio(plano, resultado)


if __name__ == "__main__":
    main()
