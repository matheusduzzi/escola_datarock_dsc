# 01. A pergunta do modelo

Os arquivos da aula «A pergunta do modelo» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `custo_das_regras.py` | A conta da seção 3: ligações, acertos, precisão, revocação e custo de quatro regras de ligação, com os preços que você der |
| `briefing-cancelamento.md` | O briefing do modelo de cancelamento, da seção 5. Ele volta na aula 16 |
| `meu-briefing.md` | A folha do exercício: o briefing do acompanhamento no primeiro mês |

O `custo_das_regras.py` lê os pedidos da base compartilhada do kit, em `../dados/loja/pedidos.csv`. Rode de dentro dessa pasta:

```bash
python3 custo_das_regras.py
python3 custo_das_regras.py --cancelamento 30
```

Os preços padrão são R$ 5 por ligação e R$ 15 por cancelamento que passa, com 600 ligações de capacidade. Troque com `--ligacao`, `--cancelamento` e `--capacidade`. Preço zero ou negativo para o programa com uma mensagem de erro.

Ele usa o pandas, que o README do kit já instala. Não precisa de internet.

O exercício usa `../dados/pessoas/admissoes.csv`. Você escreve o seu próprio código no pandas.

No Windows, troque `python3` por `py`.
