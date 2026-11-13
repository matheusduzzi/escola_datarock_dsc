# 08. Encoding de categorias

Os arquivos da aula «Encoding de categorias» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `encoding.py` | A conta da seção 3: faz one-hot, ordinal e target encoding na base de admissões, mostra o que acontece com as categorias que o treino não tem e mede a nota da equipe dentro e fora da dobra |
| `mapa-encoding-admissoes.md` | O mapa de transformação das categorias do acompanhamento, da seção 6, com as 14 colunas do treino |
| `meu-mapa.md` | A folha do exercício: o mapa de encoding do modelo de cancelamento |

O `encoding.py` lê a base compartilhada do kit, em `../dados/pessoas/admissoes.csv`. Ele usa as linhas do contrato da aula 03 e a divisão pela data da aula 06: treino até 30/06/2025, validação até 30/09/2025 e teste até 01/01/2026. O teste sai logo depois da leitura e não entra em nenhuma conta. Rode de dentro dessa pasta:

```bash
python3 encoding.py
```

Ele não tem opções e dá a mesma saída toda vez. A dobra de cada pessoa é o resto da divisão do `id_pessoa` por 5, sem sorteio. Se você rodar de outra pasta, ele para com uma mensagem que diz de onde rodar.

Ele usa o pandas, que o README do kit já instala. Não precisa de internet nem do scikit-learn.

O exercício usa `../dados/loja/pedidos_export_completo.csv`. Você escreve o seu próprio código no pandas. A função `acerto_do_par` do `encoding.py` serve para medir a nota: copie para o seu código ou use `from encoding import acerto_do_par` de dentro dessa pasta.

No Windows, troque `python3` por `py`.
