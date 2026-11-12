# Meu plano de transformação: cancelamento antes do despacho

Nome:
Data do plano:

Base: `../dados/loja/pedidos_export_completo.csv`. Treino: pedidos de janeiro a março de 2026, como na aula 05.

## Parte A. Os pedidos da Loja Exemplo

### 1. As colunas e o momento

| Coluna | Existe na hora do pedido? | Entra no modelo? | Por quê |
|---|---|---|---|
| `id_pedido` | | | |
| `data_pedido` | | | |
| `categoria` | | | |
| `forma_pagamento` | | | |
| `valor` | | | |
| `prazo_prometido_dias` | | | |
| `cliente_novo` | | | |
| `pedidos_anteriores` | | | |
| `canal` | | | |
| `dias_ate_entrega` | | | |
| `contatos_sac` | | | |

### 2. Os vazios

Cole o código e a saída:

```python

```

```

```

O que esse resultado garante, e o que ele não garante:

### 3. Os zeros

Cole o código e as duas tabelas cruzadas (no treino):

```python

```

```

```

| Zero | Quantos no treino | De onde vem | O que o plano faz |
|---|---|---|---|
| `pedidos_anteriores = 0` | | | |
| `dias_ate_entrega = 0` | | | |

### 4. Os extremos

Cole o código e a saída (limite calculado no treino):

```python

```

```

```

| Coluna | Limite no treino | Pedidos acima | % cancelaram acima | % cancelaram no resto | Mantém, corta ou corrige? Por quê |
|---|---|---|---|---|---|
| `valor` | | | | | |
| `pedidos_anteriores` | | | | | |

### 5. Onde o número é calculado

Em que meses cada número do plano é calculado:

Limite de `valor` com os seis meses, comparado com o do treino:

O que acontece com um pedido de julho acima do limite:

### 6. O aviso e a data

O que faz o plano voltar para a mesa:

Data do plano e o que obriga a escrever outro:

## Parte B. Três casos de julho

| Caso | Origem | Momento | O que o plano faz |
|---|---|---|---|
| 1. Pedidos do marketplace sem prazo | | | |
| 2. Valor em centavos no app | | | |
| 3. O pedido de R$ 18.000 da empresa | | | |
