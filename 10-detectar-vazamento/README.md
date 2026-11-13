# 10. Detectar vazamento

Os arquivos da aula «Detectar vazamento» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `vazamento.py` | A conta da seção 3: as duas preparações dos pedidos com o mesmo classificador, a varredura por coluna, um defeito por vez, a taxa e a escala calculadas com os 2400 pedidos e a versão do Rafael na hora do pedido |
| `pipeline_rafael.py` | A preparação do Rafael para o cancelamento, com uma coluna do futuro e contas feitas na base inteira, de propósito |
| `pipeline_corrigido.py` | A mesma preparação sem os vazamentos: só colunas da hora do pedido e tudo ajustado no treino |
| `testar_vazamento.py` | Os 5 testes de vazamento da seção 6. Recebe o nome da preparação: `python3 testar_vazamento.py pipeline_corrigido` |
| `classificador.py` | O classificador pronto (uma regressão logística), o acerto do par e a varredura |
| `ferramentas_teste.py` | A comparação de tabelas e o resumo dos testes, usados pelos dois arquivos de testes |
| `acompanhamento_rafael.py` | O exercício: a preparação do Rafael para a lista do dia 7, com vazamentos |
| `meus_testes.py` | O exercício: os seus testes de vazamento. Ele falha até você escrever os testes |
| `minha-nota.md` | A folha do exercício: os vazamentos, os testes, um defeito por vez e a nota para a Marta |

Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv` e as admissões de `../dados/pessoas/admissoes.csv`. Treino dos pedidos: janeiro a março de 2026; validação: abril e maio; junho é o teste e não entra em nenhuma medida. Rode de dentro dessa pasta:

```bash
python3 vazamento.py
python3 testar_vazamento.py pipeline_rafael
python3 testar_vazamento.py pipeline_corrigido
```

O primeiro dá a mesma saída toda vez. Os testes contra o `pipeline_rafael` falham de propósito e terminam com código 1; contra o `pipeline_corrigido`, os 5 passam. Se você rodar de outra pasta, os programas param com uma mensagem que diz de onde rodar.

O exercício:

```bash
python3 acompanhamento_rafael.py
python3 meus_testes.py acompanhamento_rafael
```

Antes de você escrever os testes, o segundo comando termina com `0 de 1 testes passaram` e a mensagem `apague esse teste e escreva os seus`. É o ponto de partida.

Tudo usa o pandas e o NumPy, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn.

No Windows, troque `python3` por `py`.
