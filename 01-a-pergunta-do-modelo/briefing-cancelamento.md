# Briefing: o modelo de cancelamento

O briefing da aula «A pergunta do modelo». Ele volta na aula 16, quando a régua é aplicada ao teste final.

**Pergunta.** Na hora do pedido, este pedido vai ser cancelado?

**Quem usa e quando.** A equipe de atendimento do Caio, antes do despacho. O modelo só usa o que existe quando o pedido entra.

**Ação.** A equipe liga para os pedidos marcados e confirma. No máximo 100 ligações por mês, 1 de cada 4 pedidos.

**Os dois erros.** Ligação à toa: R$ 5 de tempo da equipe. Cancelamento que passa sem ligação: R$ 15 de separação e volta ao estoque. Preços da gerente e do Caio. Ponto de empate: 33,3% de precisão.

**Regra a vencer.** Ligar para todo pedido no boleto. No semestre: precisão 37,1%, revocação 32,5%, R$ 6.775.

**Uso se, no teste final, olhado uma vez:** precisão de pelo menos 40%; revocação de pelo menos 40%; custo menor que o da regra do boleto nos mesmos pedidos; e no máximo 1 ligação para cada 4 pedidos.

**Não uso** se qualquer uma falhar. Acurácia não entra na decisão. Se eu mudar o corte do modelo, ele sai da validação, nunca do teste.

**O que o modelo não decide.** Ele não cancela pedido nem recusa boleto. Ele só monta a lista de ligações.

**Escrito em 3 de julho de 2026**, antes de treinar qualquer modelo. Se um preço mudar por motivo da loja, eu escrevo um briefing novo, com data e motivo, antes do teste.

Os números da regra do boleto saem de `python3 custo_das_regras.py`, nessa mesma pasta.
