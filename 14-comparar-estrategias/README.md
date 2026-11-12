# 14. Comparar estratégias

Os arquivos da aula «Comparar estratégias» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `comparar.py` | O experimento da seção 3: as cinco estratégias mexendo só no treino, medidas nos mesmos pedidos da validação, com a nota como sai e corrigida, e os 20 sorteios. Grava e refaz o registro |
| `experimento.json` | O registro do experimento, gravado com `python3 comparar.py --registrar`: dados, parâmetros, versões e resultados |
| `estrategias.py` | As cinco estratégias (nenhuma, peso de classe, subamostragem, sobreamostragem e SMOTE), o treino com pesos e a correção da nota |
| `testar_estrategias.py` | Os testes do `estrategias.py` |
| `pipeline_corrigido.py` | A preparação dos pedidos sem vazamento, a mesma da aula 10 |
| `classificador.py` | O classificador pronto (uma regressão logística) e o acerto do par, os mesmos da aula 10 |
| `pipeline_pessoas.py` | O pipeline do acompanhamento, o mesmo `pipeline.py` da aula 09 |
| `experimento_rh.py` | O exercício: as estratégias no acompanhamento do RH. Ele para com `NotImplementedError` até você escrever as duas funções |
| `testar_experimento_rh.py` | Os testes das duas funções do exercício, com casos pequenos montados no próprio arquivo |
| `minha-comparacao.md` | A folha do exercício: a saída, a leitura e a recomendação para a Marta |

Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv` e as admissões de `../dados/pessoas/admissoes.csv`. Pedidos: treino de janeiro a março de 2026, validação em abril e maio; junho é o teste e não entra em nenhuma conta. Admissões: treino até 30/06/2025, validação de julho a setembro de 2025; o teste fica fechado. Rode de dentro dessa pasta:

```bash
python3 comparar.py
python3 comparar.py --refazer
python3 comparar.py --sorteio 7 --refazer
python3 comparar.py --validacao-reamostrada
python3 testar_estrategias.py
```

O primeiro dá a mesma saída toda vez. O segundo compara a rodada com o `experimento.json` e termina com "igual ao registro". O terceiro troca o sorteio e termina com a lista de diferenças e o código 1, de propósito. Com `--registrar`, o `comparar.py` grava um `experimento.json` novo no lugar do que veio no kit.

Se a sua versão do Python, do pandas ou do NumPy for outra, o `--refazer` mostra um aviso de versão. Se algum número mudar, ele mostra qual.

O exercício:

```bash
python3 testar_experimento_rh.py
python3 experimento_rh.py --registrar
python3 experimento_rh.py --refazer
```

Antes de você escrever a `avaliar()` e a `conferir()`, os testes terminam com `FAILED (errors=10)` e código 1, e o `experimento_rh.py` para com `NotImplementedError`. É o ponto de partida. Depois, os testes terminam com `OK`.

Tudo usa o pandas e o NumPy, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn: as estratégias estão escritas no `estrategias.py`, com o mesmo classificador das aulas anteriores. O experimento inteiro leva alguns segundos. Se você rodar de outra pasta, os programas param com uma mensagem que diz de onde rodar.

No Windows, troque `python3` por `py`.
