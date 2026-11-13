# Meu contrato do rótulo do cancelamento

Nome:
Data em que escrevi:

Base: `../dados/loja/pedidos_export_completo.csv`. Cole embaixo de cada parte o código que você rodou e a saída.

## 1. A linha e o momento

O que é uma linha:

Quando a previsão é feita:

A mesma cliente em mais de uma linha:

## 2. O rótulo

Pedidos com `cancelado` igual a 1:

Desses, com `dias_ate_entrega` maior que zero, e o que eles são:

O que eu faço com eles, e por quê:

## 3. O horizonte e a maturação

Atraso nos pedidos que saíram para entrega (menor e maior):

A resposta de um pedido existe a partir de:

O export pode ter sido tirado a partir de:

Num export de 30/06/2026, pedidos que ainda poderiam estar sem resposta:

## 4. As colunas do momento

| Coluna | Entra, fica fora ou perguntar | Motivo |
|---|---|---|
| `id_pedido` | | |
| `data_pedido` | | |
| `categoria` | | |
| `forma_pagamento` | | |
| `valor` | | |
| `prazo_prometido_dias` | | |
| `cliente_novo` | | |
| `pedidos_anteriores` | | |
| `canal` | | |
| `dias_ate_entrega` | | |
| `contatos_sac` | | |
| `cancelado` | | |

## 5. Os casos de fronteira

| `id_pedido` | O que tem de especial | Rótulo | No treino? |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |

## 6. A data

Escrito em:

O que me obriga a escrever outro contrato:
