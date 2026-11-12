# 11. Baseline e métricas

Os arquivos da aula «Baseline e métricas» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `avaliar.py` | A tabela de avaliação da seção 3: nunca liga, liga para todos, a regra do boleto e o classificador em dois cortes, nos mesmos pedidos da validação, com a matriz, a precisão, a revocação e o custo |
| `pipeline_corrigido.py` | A preparação dos pedidos sem vazamento, a mesma da aula 10 |
| `classificador.py` | O classificador pronto (uma regressão logística) e o acerto do par, os mesmos da aula 10 |
| `pipeline_pessoas.py` | O pipeline do acompanhamento, o mesmo `pipeline.py` da aula 09 |
| `avaliacao_rh.py` | O exercício: a tabela de avaliação do acompanhamento. Ele para com `NotImplementedError` até você escrever as duas funções |
| `testar_avaliacao_rh.py` | Os testes das duas funções do exercício, com casos pequenos feitos à mão |
| `minha-tabela.md` | A folha do exercício: a tabela, a leitura e a recomendação para a Marta |

Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv` e as admissões de `../dados/pessoas/admissoes.csv`. Pedidos: treino de janeiro a março de 2026, validação em abril e maio; junho é o teste e não entra em nenhuma conta. Admissões: treino até 30/06/2025, validação de julho a setembro de 2025; o teste fica fechado. Rode de dentro dessa pasta:

```bash
python3 avaliar.py
python3 avaliar.py --varrer
python3 avaliar.py --cancelamento 30
```

Os três dão a mesma saída toda vez. `--ligacao` e `--cancelamento` trocam os preços; `--varrer` mostra o custo do classificador em vários cortes.

O exercício:

```bash
python3 testar_avaliacao_rh.py
python3 avaliacao_rh.py
```

Antes de você escrever a `linha()` e as `regras()`, os testes terminam com `FAILED (errors=6)` e código 1, e o `avaliacao_rh.py` para com `NotImplementedError`. É o ponto de partida. Depois, os testes terminam com `OK`.

Tudo usa o pandas e o NumPy, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn. Se você rodar de outra pasta, os programas param com uma mensagem que diz de onde rodar.

No Windows, troque `python3` por `py`.
