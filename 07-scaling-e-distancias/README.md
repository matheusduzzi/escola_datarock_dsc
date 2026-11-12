# 07. Scaling e distâncias

Os arquivos da aula «Scaling e distâncias» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `escalas.py` | A conta da seção 3: calcula o MinMax, o Standard e o Robust no treino das admissões e mostra quanto cada coluna pesa na distância, quem são os vizinhos de uma pessoa e o que muda numa árvore |
| `escolha-escala-admissoes.md` | A escolha de escala do acompanhamento, da seção 6 |
| `minha-escolha.md` | A folha do exercício: a escolha de escala do modelo de cancelamento |

O `escalas.py` lê a base compartilhada do kit, em `../dados/pessoas/admissoes.csv`. Ele usa as linhas do contrato da aula 03, a divisão pela data da aula 06 (treino até 30/06/2025, validação até 30/09/2025 e teste até 01/01/2026) e o plano de transformação da aula 06. Rode de dentro dessa pasta:

```bash
python3 escalas.py
```

Ele não tem opções e dá a mesma saída toda vez. Se você rodar de outra pasta, ele para com uma mensagem que diz de onde rodar. Na prática guiada, você importa duas funções dele no `python3`, sempre de dentro dessa pasta.

Ele usa o pandas e o NumPy, que o README do kit já instala. Não precisa de internet nem do scikit-learn: as três escalas são contas de duas linhas, escritas no próprio programa.

O exercício usa `../dados/loja/pedidos_export_completo.csv`. Você escreve o seu próprio código no pandas e no NumPy.

No Windows, troque `python3` por `py`.
