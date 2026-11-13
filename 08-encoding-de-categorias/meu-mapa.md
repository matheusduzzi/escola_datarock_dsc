# Meu mapa de encoding: cancelamento antes do despacho

Nome:
Data do mapa:

Base: `../dados/loja/pedidos_export_completo.csv`. Treino: pedidos de janeiro a março de 2026. Validação: abril e maio. Teste: junho, fechado. A divisão é a da aula 05.

## Parte A. As categorias dos pedidos

### 1. As categorias no treino

Cole o código e a saída:

```python

```

```

```

| Coluna | Categorias no treino | Pedidos na menor | % cancelou, da menor para a maior taxa |
|---|---|---|---|
| `categoria` | | | |
| `forma_pagamento` | | | |
| `canal` | | | |

### 2. One-hot

Cole o código e a saída (colunas do treino e o pedido de julho do marketplace):

```python

```

```

```

Quantas colunas o treino cria, e quais:

O que acontece com o pedido do marketplace, e o que o mapa faz com ele:

### 3. Ordinal

Alguma dessas três colunas tem ordem de verdade? Por quê:

O que o `cat.codes` dá para `forma_pagamento`, e por que isso não serve para um modelo que lê o número como quantidade:

### 4. Target encoding fora da dobra

Combinação: `categoria` + `forma_pagamento` + `canal` + `cliente_novo`.

Cole o código e a saída:

```python

```

```

```

| Como a nota foi calculada | Acerto do par no treino | Acerto do par na validação |
|---|---|---|
| média de todo o treino | | |
| fora da dobra, 5 dobras | | |

Qual número do treino promete o que a validação entrega? Por quê:

A combinação entra no modelo? Por quê:

### 5. O mapa

| Coluna | Jeito | Por quê | Onde o número é calculado | Categoria que o treino não tem |
|---|---|---|---|---|
| `categoria` | | | | |
| `forma_pagamento` | | | | |
| `canal` | | | | |
| `cliente_novo` | | | | |
| combinação | | | | |

Como você sabe que nenhum número do mapa usa o teste:

O que faz o mapa voltar para a mesa:

Data do mapa e o que obriga a escrever outro:

## Parte B. Três casos de julho

| Caso | Jeito | Ordem ou taxa usada, e de onde sai | O que acontece no uso e com a categoria nova |
|---|---|---|---|
| 1. Pedidos do marketplace | | | |
| 2. A faixa de fidelidade | | | |
| 3. O CEP de entrega | | | |
