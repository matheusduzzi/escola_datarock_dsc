# 09. Pipeline para dados de pessoas

Os arquivos da aula «Pipeline para dados de pessoas» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `pipeline.py` | O pipeline do acompanhamento no primeiro mês, com `ajustar(treino)` e `aplicar(params, pessoas)`, e a conta da seção 3: o que ele guarda, a preparação que recalcula a cada base, os avisos das pessoas novas e uma pessoa por vez contra o lote |
| `testar_pipeline.py` | Os 14 testes do pipeline, da seção 6 |
| `meu_pipeline.py` | O exercício: o pipeline do cancelamento, com `ajustar` e `aplicar` para você escrever |
| `testar_meu_pipeline.py` | Os 9 testes do exercício. Eles falham até você escrever as duas funções |
| `minha-nota.md` | A folha do exercício: a saída dos testes e a nota para a gerente |

O `pipeline.py` lê a base compartilhada do kit, em `../dados/pessoas/admissoes.csv`. Ele usa as linhas do contrato da aula 03 e a divisão pela data: treino até 30/06/2025, validação até 30/09/2025 e teste até 01/01/2026. O teste sai logo depois da leitura e não entra em nenhuma conta. Rode de dentro dessa pasta:

```bash
python3 pipeline.py
python3 testar_pipeline.py
```

Os dois não têm opções e dão a mesma saída toda vez; só o tempo no fim dos testes muda. Se você rodar de outra pasta, eles param com uma mensagem que diz de onde rodar.

O exercício usa `../dados/loja/pedidos_export_completo.csv`:

```bash
python3 testar_meu_pipeline.py
python3 meu_pipeline.py
```

Antes de você escrever o `ajustar` e o `aplicar`, os testes terminam com `FAILED (errors=1)` e `NotImplementedError: escreva o ajustar`. É o ponto de partida.

Tudo usa o pandas, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn.

No Windows, troque `python3` por `py`.
