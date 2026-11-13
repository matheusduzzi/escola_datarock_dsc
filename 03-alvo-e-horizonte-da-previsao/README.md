# 03. Alvo e horizonte da previsão

Os arquivos da aula «Alvo e horizonte da previsão» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `rotulo.py` | A conta da seção 3: monta o rótulo "saiu até H dias" pelas datas, mostra quem já tem resposta em cada trimestre e compara as quatro contas da taxa de saída |
| `contrato-alvo-admissoes.md` | O contrato do alvo do acompanhamento, da seção 6, com os casos de fronteira |
| `meu-contrato.md` | A folha do exercício: o contrato do rótulo do cancelamento |

O `rotulo.py` lê a base compartilhada do kit, em `../dados/pessoas/admissoes.csv`. Rode de dentro dessa pasta:

```bash
python3 rotulo.py
python3 rotulo.py --horizonte 90
```

O padrão é horizonte de 180 dias, com a lista do RH no dia 7. Troque com `--horizonte` e `--decisao`. Valor zero, negativo ou que não seja um número inteiro para o programa com uma mensagem de erro. O dia da lista precisa vir antes do fim do horizonte.

Ele usa o pandas, que o README do kit já instala. Não precisa de internet.

O exercício usa `../dados/loja/pedidos_export_completo.csv`. Você escreve o seu próprio código no pandas.

No Windows, troque `python3` por `py`.
