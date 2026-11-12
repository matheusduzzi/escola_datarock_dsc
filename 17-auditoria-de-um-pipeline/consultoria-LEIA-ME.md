# Entrega da consultoria: dois modelos para a Loja Exemplo

Versão de 20/07/2026. Os dois modelos usam o classificador que a loja já usa (`classificador.py`), para a comparação ser justa.

## Cancelamento de pedidos

Programa: `consultoria_cancelamento.py`. Base: `pedidos_export_completo.csv`, impressão digital 77a72e1c0cc9.

Resultado no teste, 30% dos pedidos, com o corte da loja (0,333): precisão 61,9%, revocação 55,3%, acerto do par 82,6%.

A lista que a loja usa hoje tem precisão de 53,0% e revocação de 46,7%. A nossa pega mais cancelamentos e erra menos ligações. O ganho vem da coluna nova, a taxa de cancelamento do perfil do pedido.

## Acompanhamento no primeiro mês

Programa: `consultoria_acompanhamento.py`. Base: `admissoes.csv`, impressão digital 32694dc5c8a1.

Resultado no teste, 30% das pessoas, com o corte do RH (0,32): acerto do par 66,5%.

O acerto do par do modelo que o RH tem hoje é 60,2%. O nosso ordena melhor as pessoas. O ganho vem da taxa de saída da equipe (loja e cargo).
