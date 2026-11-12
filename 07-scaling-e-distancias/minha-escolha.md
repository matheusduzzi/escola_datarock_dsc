# Minha escolha de escala: o modelo de cancelamento

Salve uma cópia com o seu nome. Cole o código de cada conta logo abaixo da resposta.

Base: `../dados/loja/pedidos_export_completo.csv`. Treino de janeiro a março de 2026. Colunas: `valor`, `prazo_prometido_dias`, `pedidos_anteriores`, `cliente_novo`.

## Parte A. A escala do modelo de vizinhos

**1. Os números de cada escala, no treino**

| Escala | `valor` | `prazo_prometido_dias` | `pedidos_anteriores` | `cliente_novo` |
|---|---|---|---|---|
| MinMax: tira / divide por | | | | |
| Standard: tira / divide por | | | | |
| Robust: tira / divide por | | | | |

**2. O peso de cada coluna na distância**

| Escala | `valor` | `prazo_prometido_dias` | `pedidos_anteriores` | `cliente_novo` | Quem manda e por quê |
|---|---|---|---|---|---|
| sem escala | | | | | |
| MinMax | | | | | |
| Standard | | | | | |
| Robust | | | | | |

**3. Os extremos**

Onde o valor mediano cai no MinMax:

O que isso faz com o peso do valor:

**4. A escolha**

Escala do modelo de vizinhos:

Peso de cada coluna, e por que serve para o modelo:

Por que as outras não servem:

**5. Se o modelo for uma árvore**

| Versão | Corte de R$ 913,19 convertido | Pedidos acima | Cancelados |
|---|---|---|---|
| sem escala | | | |
| MinMax | | | |
| Standard | | | |
| Robust | | | |

A árvore precisa de escala?

**6. Onde o número é calculado, o aviso e a data**

De que meses saem os números:

O que acontece com um pedido de julho:

O que faz a escolha voltar para a mesa:

Data:

## Parte B. O pedido da empresa

R$ 18.000, prazo de 10 dias, cliente novo, nenhum pedido anterior.

| Escala | O valor vira | O maior valor do treino vira |
|---|---|---|
| MinMax | | |
| Standard | | |
| Robust | | |

Os 25 vizinhos, com a escala que eu escolhi (o que eles têm em comum):

O que a nota dele quer dizer:

O que a escolha faz com um pedido assim:
