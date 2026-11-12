# 06. Valores vazios e extremos

Os arquivos da aula «Valores vazios e extremos» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `vazios_extremos.py` | A conta da seção 3: mostra onde a base de admissões tem distância vazia e salário ou distância extremos, de onde vem cada um e que números o plano calcula no treino |
| `plano-transformacao-admissoes.md` | O plano de transformação do acompanhamento, da seção 6 |
| `meu-plano.md` | A folha do exercício: o plano de transformação do modelo de cancelamento |

O `vazios_extremos.py` lê a base compartilhada do kit, em `../dados/pessoas/admissoes.csv`. Ele usa as linhas do contrato da aula 03 e a divisão pela data do exercício da aula 05: treino até 30/06/2025, validação até 30/09/2025 e teste até 01/01/2026. Rode de dentro dessa pasta:

```bash
python3 vazios_extremos.py
```

Ele não tem opções e dá a mesma saída toda vez. Se você rodar de outra pasta, ele para com uma mensagem que diz de onde rodar.

Ele usa o pandas, que o README do kit já instala. Não precisa de internet nem do scikit-learn.

O exercício usa `../dados/loja/pedidos_export_completo.csv`. Você escreve o seu próprio código no pandas.

No Windows, troque `python3` por `py`.
