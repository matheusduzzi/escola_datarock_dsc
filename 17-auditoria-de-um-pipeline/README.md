# 17. Auditoria de um pipeline

Os arquivos da aula «Auditoria de um pipeline» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `consultoria-LEIA-ME.md` | O que a consultoria entregou: os dois modelos, a base que eles usaram e o resultado que eles dizem ter |
| `consultoria_cancelamento.py` | O modelo de cancelamento da consultoria, do jeito que eles entregaram |
| `consultoria_acompanhamento.py` | O modelo do acompanhamento da consultoria, do jeito que eles entregaram. É o projeto do exercício |
| `auditar.py` | A auditoria da aula, em quatro passos: reproduzir, achados, consertos e checar |
| `sorteios.py` | O modelo de cancelamento da consultoria com outros 19 sorteios do teste, para ver quanto o número deles muda |
| `consertos.py` | O modelo de cancelamento da consultoria com um conserto de cada vez, somados |
| `auditoria.py` | As peças comuns: impressão digital, manifesto, a medida da lista e a contagem de linhas que mudaram |
| `parecer.md` | O parecer da aula sobre o modelo de cancelamento |
| `pipeline_corrigido.py` | A preparação dos pedidos sem vazamento, a mesma da aula 10 |
| `classificador.py` | O classificador pronto (uma regressão logística) e o acerto do par, os mesmos da aula 10 |
| `pipeline_pessoas.py` | O pipeline do acompanhamento, o mesmo `pipeline.py` da aula 09 |
| `auditar_rh.py` | O exercício: a mesma auditoria para o modelo do acompanhamento |
| `achados_rh.py` | O exercício: as três perguntas que você escreve |
| `consertar_rh.py` | O exercício: o modelo do acompanhamento com os consertos que você escreve |
| `testar_achados_rh.py` | Os testes do exercício, com casos pequenos feitos à mão e os três projetos |
| `meu-parecer.md` | A folha do exercício: o seu parecer para a Marta |

Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv` e as admissões de `../dados/pessoas/admissoes.csv`. Rode de dentro dessa pasta:

```bash
python3 consultoria_cancelamento.py
python3 auditar.py reproduzir
python3 auditar.py achados
python3 auditar.py consertos
python3 auditar.py checar
python3 sorteios.py
```

O primeiro roda o projeto deles sozinho. Os três passos seguintes gravam a saída em `auditoria/` e anotam em `auditoria/manifesto.json` a impressão digital de cada arquivo que leram e de cada saída. O `checar` refaz os três passos e compara com o manifesto. Se algum arquivo mudou, ele diz qual e termina com código 1. O `sorteios.py` roda o projeto deles com o teste sorteado de 20 jeitos.

Num projeto de verdade, a pasta `auditoria/` e o `parecer.md` entram juntos num commit do Git. Quem ler depois sabe de que arquivos saiu cada número.

O exercício:

```bash
python3 auditar_rh.py reproduzir
python3 testar_achados_rh.py
python3 auditar_rh.py achados
python3 auditar_rh.py consertos
python3 auditar_rh.py checar
```

O `reproduzir` do exercício já funciona. Antes de você escrever as três `checar_*()` e o `preparar()` do `consertar_rh.py`, os testes terminam com `FAILED (errors=14)` e código 1, e os passos `achados` e `consertos` param com a mensagem do que ainda não foi escrito, sem anotar nada. É o ponto de partida. Depois, os testes terminam com `OK`.

Se você mudar o `achados_rh.py` ou o `consertar_rh.py` depois de rodar um passo, o `checar` avisa. Rode de novo o passo que leu o arquivo mudado e depois o `checar`.

Tudo usa o pandas e o NumPy, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn. Se você rodar de outra pasta, os programas param com uma mensagem que diz de onde rodar.

No Windows, troque `python3` por `py`.
