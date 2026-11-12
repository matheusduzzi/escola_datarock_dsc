# Parecer: o modelo de cancelamento da consultoria

O parecer da seção 7 da aula «Auditoria de um pipeline». Os números saem de `python3 auditar.py`, nessa pasta.

**Pergunta.** A gerente, em 21 de julho de 2026: a lista da consultoria, com precisão de 61,9% e revocação de 55,3%, é melhor que a nossa, com 53,0% e 46,7%? Troco antes do piloto?

**Resposta.** Não troca. Os números deles saem de três defeitos. Com os três consertados, o mesmo modelo dá 44,6% de precisão e 38,0% de revocação em abril e maio. Nos mesmos 795 pedidos, ele custa R$ 2.210, e a nossa lista R$ 2.105.

**Reprodução.** Rodei `consultoria_cancelamento.py`, impressão digital e1614d528c91, na base 77a72e1c0cc9, a mesma do LEIA-ME deles. Saiu o número deles: 126 ligações, 78 certas, precisão 61,9%, revocação 55,3%, acerto do par 82,6%.

**Alvo.** O rótulo deles é "dias até a entrega igual a zero". Os 22 pedidos cancelados depois de sair para a entrega ficam com rótulo 0. Esses 22 também custam R$ 15 cada. A lista deles responde a outra pergunta.

**Divisão.** O teste deles é sorteado entre janeiro e junho. Todos os 1680 pedidos do treino são do primeiro dia do teste em diante, e 318 são de junho, o nosso teste. O modelo deles já viu junho e não pode mais ser medido nele.

**Transformação.** A escala, as categorias e a taxa do perfil saem dos 2400 pedidos, com o rótulo de todos. Trocar o resultado só dos pedidos do teste muda 1491 das 1680 linhas do treino e 672 das 720 do próprio teste. A taxa do perfil usa o rótulo do próprio pedido.

**Um conserto de cada vez.** Mesmo classificador, mesmo corte (0,333).

| Passo | Medido em | Precisão | Revocação | Custo |
|---|---|---|---|---|
| Como entregue | 720 sorteados | 61,9% | 55,3% | |
| Mais o alvo | 720 sorteados | 65,6% | 57,7% | |
| Mais a divisão por data | abril e maio, 795 | 59,3% | 49,1% | R$ 1.920 |
| Mais a preparação só no treino | abril e maio, 795 | 44,6% | 38,0% | R$ 2.210 |
| A nossa lista | abril e maio, 795 | 50,8% | 40,5% | R$ 2.105 |

Não ligar para ninguém em abril e maio custa R$ 2.445. O quanto cada defeito pesa depende da ordem dos consertos. Por isso este parecer não divide a diferença entre os três.

**O que não muda.** A decisão da aula 16 continua: uso, pela régua de 3 de julho, medida em junho uma vez. Este parecer não usa junho. A nota de decisão vai junto.

**O que eu não sei.** Se a taxa do perfil pagaria com mais meses de treino. Hoje a metade dos perfis tem 4 pedidos ou menos no treino. A taxa de um grupo tão pequeno muda muito de um mês para outro.

**Próximo passo e quem decide.** Se a consultoria quer a taxa do perfil, ela manda um plano novo, com data, ajustado só no treino. Ele é medido em pedidos que ninguém abriu, de julho em diante. Trocar de lista é decisão da gerente.

**Arquivos.** `auditoria/manifesto.json`, impressão digital 542613946787. `python3 auditar.py checar` refaz os três passos e compara. A pasta `auditoria/`, este parecer e a nota de decisão vão no mesmo commit.
