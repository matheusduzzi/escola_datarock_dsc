# 16. Decidir pelo critério

Os arquivos da aula «Decidir pelo critério» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `decidir.py` | O programa da aula: mostra o plano, abre o teste de junho uma vez, aplica a régua do briefing e anota a abertura em `abertura.json`. Recusa um plano diferente depois da abertura |
| `regua.json` | O plano do cancelamento, escrito antes do teste: preços, classificador, corte e as quatro condições do briefing da aula 01 |
| `regua-do-rafael.json` | O plano do Rafael, com o corte 0,35 escolhido depois de ver junho. Serve para ver a recusa da seção 4 |
| `nota-de-decisao.md` | A nota de decisão da aula, com os números da abertura |
| `pipeline_corrigido.py` | A preparação dos pedidos sem vazamento, a mesma da aula 10 |
| `classificador.py` | O classificador pronto (uma regressão logística) e o acerto do par, os mesmos da aula 10 |
| `pipeline_pessoas.py` | O pipeline do acompanhamento, o mesmo `pipeline.py` da aula 09 |
| `decidir_rh.py` | O exercício: abrir o teste do acompanhamento uma vez e aplicar a régua da Marta. Ele não abre o teste até você escrever a `aplicar_regua()` |
| `regua_rh.json` | O plano do acompanhamento, com a régua que a Marta assinou |
| `regua-rh-do-rafael.json` | O plano do Rafael para o acompanhamento, com o corte e a régua trocados depois de ver o teste |
| `testar_decidir_rh.py` | Os testes da `aplicar_regua()`, com casos pequenos feitos à mão |
| `minha-nota.md` | A folha do exercício: as saídas, a proposta do Rafael e a nota para a Marta |

Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv` e as admissões de `../dados/pessoas/admissoes.csv`. Rode de dentro dessa pasta:

```bash
python3 decidir.py
python3 decidir.py --abrir
python3 decidir.py --abrir
python3 decidir.py --abrir --regua regua-do-rafael.json
```

O primeiro só lê o plano e não abre nenhum pedido. O segundo abre junho, mostra a régua aplicada e grava o `abertura.json`. O terceiro refaz a conta, compara com a anotada e mostra a mesma tabela. O quarto termina com "recusado", a lista do que mudou e o código 1, de propósito.

Se quiser ver a abertura do zero, apague o `abertura.json` e rode de novo. Num projeto de verdade, esse arquivo e a nota de decisão entram juntos no Git, e apagar o arquivo fica à vista no histórico.

O exercício:

```bash
python3 testar_decidir_rh.py
python3 decidir_rh.py
python3 decidir_rh.py --abrir
python3 decidir_rh.py --abrir --regua regua-rh-do-rafael.json
```

Antes de você escrever a `aplicar_regua()`, os testes terminam com `FAILED (errors=9)` e código 1, e o `decidir_rh.py --abrir` para com a mensagem "a aplicar_regua() ainda não foi escrita", sem abrir o teste. É o ponto de partida. Depois, os testes terminam com `OK`. A abertura do exercício fica anotada em `abertura_rh.json`.

Tudo usa o pandas e o NumPy, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn. Se você rodar de outra pasta, os programas param com uma mensagem que diz de onde rodar.

No Windows, troque `python3` por `py`.
