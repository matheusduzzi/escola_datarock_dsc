"""Peças comuns das duas auditorias: impressão digital, manifesto, medida da lista e comparação.

Aula «Auditoria de um pipeline» do curso ML: preparação e validação.

- digital(caminho): o SHA-256 do arquivo, com o fim de linha igual em qualquer sistema.
- linhas_que_mudaram(antes, depois): quantas linhas de uma tabela mudaram entre duas rodadas.
- medir(y, nota, corte): a matriz da lista e as contas da aula 11.
- Manifesto: o arquivo que guarda a impressão digital de cada entrada e de cada saída da auditoria.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from classificador import acerto_do_par


def digital(caminho):
    return hashlib.sha256(Path(caminho).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def digital_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def linhas_que_mudaram(antes, depois):
    """Linhas com algum valor diferente. Outras colunas ou outros ids contam como tudo mudado."""
    if list(antes.columns) != list(depois.columns) or not antes.index.equals(depois.index):
        return max(len(antes), len(depois))
    a = antes.to_numpy(dtype=float)
    b = depois.to_numpy(dtype=float)
    diferente = ~np.isclose(a, b, rtol=0, atol=1e-9, equal_nan=True)
    return int(diferente.any(axis=1).sum())


def medir(y, nota, corte, acerto=None, erro=None):
    """VP, FP, FN, ligações, precisão, revocação e acerto do par da lista nota > corte.

    acerto e erro, se vierem, são os valores em reais de cada acerto e de cada ligação
    (no RH, 750 e 240) e entram como saldo contra não fazer nada.
    """
    y = pd.Series(np.asarray(y, dtype=int))
    nota = pd.Series(np.asarray(nota, dtype=float))
    lista = nota > corte
    vp = int((lista & (y == 1)).sum())
    fp = int((lista & (y == 0)).sum())
    fn = int((~lista & (y == 1)).sum())
    m = {"n": len(y), "positivos": int(y.sum()), "lista": vp + fp, "vp": vp, "fp": fp, "fn": fn,
         "precisao": vp / (vp + fp) if vp + fp else None, "revocacao": vp / (vp + fn) if vp + fn else None,
         "acerto_do_par": acerto_do_par(nota, y)}
    if acerto is not None:
        m["saldo"] = acerto * vp - erro * (vp + fp)
    return m


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x):
    return "-" if x is None else num(100 * x) + "%"


def reais(x):
    return ("-R$ " if x < 0 else "R$ ") + num(abs(x), 0)


class Manifesto:
    """manifesto.json: para cada passo, a impressão digital das entradas que ele leu e da saída."""

    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.caminho = self.pasta / "manifesto.json"

    def ler(self):
        if not self.caminho.is_file():
            return {}
        return json.loads(self.caminho.read_text(encoding="utf-8"))

    def anotar(self, entradas, nome_saida, texto):
        """Grava a saída de um passo e põe no manifesto as entradas e a saída desse passo."""
        self.pasta.mkdir(exist_ok=True)
        (self.pasta / nome_saida).write_text(texto, encoding="utf-8")
        m = self.ler()
        m[nome_saida] = {"entradas": {str(a): digital(a) for a in sorted(map(str, entradas))},
                         "saida": digital_texto(texto)}
        m = dict(sorted(m.items()))
        self.caminho.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return self.impressao(m)

    @staticmethod
    def impressao(m):
        return digital_texto(json.dumps(m, ensure_ascii=False, sort_keys=True))[:12]

    def checar(self, passos):
        """Confere as entradas de cada passo e refaz a saída. passos: {nome_saida: função que retorna o texto}."""
        m = self.ler()
        linhas = [f"manifesto: {self.caminho.as_posix()}, impressão digital {self.impressao(m)}"]
        tudo = True
        for nome, refazer in passos.items():
            if nome not in m:
                linhas.append(f"  {nome:<16}não está no manifesto")
                tudo = False
                continue
            entradas = m[nome]["entradas"]
            mudou = [a for a, d in entradas.items() if not Path(a).is_file() or digital(a) != d]
            igual = digital_texto(refazer()) == m[nome]["saida"]
            tudo = tudo and igual and not mudou
            txt = f"{len(entradas)} entradas iguais" if not mudou else "entrada diferente: " + ", ".join(mudou)
            linhas.append(f"  {nome:<16}{txt}; saída refeita {'igual' if igual else 'diferente'}")
        return tudo, "\n".join(linhas)
