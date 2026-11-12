# Diagnóstico: por onde começar em ML: preparação e validação

A gerente da Loja Exemplo quer que o atendimento ligue antes do despacho para os pedidos com cara de cancelamento. Antes de ela pedir um modelo, alguém já tinha testado uma regra de bolso: "boleto cancela mais". Ela me mandou os números da regra e duas frases: "a regra acerta 74%, então funciona" e "o modelo novo deu 83% contra 81% do antigo, então é melhor". Antes de responder, eu refiz as contas. As cinco tarefas abaixo são essas contas e o código que eu usei.

Elas pedem o que o curso usa desde a primeira aula: proporção com o denominador certo, uma função de pandas que não perde linha, um teste lido antes de rodar e a leitura da variação de uma amostra. O diagnóstico não é prova e não tem nota. Ele mostra por onde você começa. Anote na [folha de respostas](minhas-respostas.md) a conta que fez, o comando que rodou e a saída que apareceu. Só depois compare com as respostas.

As tarefas 1 e 5 são de lápis e papel ou calculadora. As tarefas 2, 3 e 4 rodam de dentro da pasta `00-apresentacao/`:

```bash
cd 00-apresentacao
python3 tarefa4.py
```

No Windows, troque `python3` por `py`.

## Tarefa 1. Quantos a regra acerta, e acerta o quê

A regra marca todo pedido pago com boleto. Num mês com 600 pedidos, 117 foram cancelados. A regra marcou 110 pedidos. Desses 110, 35 foram cancelados de verdade.

1. Monte a tabela com quatro contagens: marcados que cancelaram, marcados que foram entregues, não marcados que cancelaram e não marcados que foram entregues.
2. De cada 100 pedidos marcados, quantos cancelaram?
3. De cada 100 pedidos cancelados, quantos a regra marcou?
4. Que porcentagem dos 600 pedidos a regra classificou certo? E quanto acerta quem diz "não cancela" para todo pedido?
5. A equipe vai ligar para os 110 marcados. Qual das suas contas diz quantas ligações valem a pena? E qual diz quantos cancelamentos passam sem ligação?

## Tarefa 2. Uma função que não perde pedido

`dados/pedidos_marco.csv` tem 20 pedidos de março. Uma linha é um pedido. Em dois deles a forma de pagamento ficou vazia.

Em `tarefa2.py`, escreva a função `taxa_por_grupo(df, coluna)`. Ela retorna uma tabela com uma linha por valor de `coluna` e estas colunas:

| Coluna | O que é |
|---|---|
| a própria `coluna` | o grupo; valor vazio vira `sem informação` |
| `pedidos` | quantos pedidos o grupo tem |
| `cancelados` | quantos foram cancelados |
| `taxa_pct` | cancelados dividido por pedidos, em porcentagem, com uma casa decimal |

As linhas saem em ordem alfabética do grupo. Depois rode os testes:

```bash
python3 tarefa2.py
python3 testar_tarefa2.py
```

Enquanto a função não existe, os dois comandos param com `NotImplementedError`. Anote na folha:

1. A tabela que `tarefa2.py` mostrou.
2. Quantos pedidos somem se você agrupar direto com `groupby("forma_pagamento")`, sem tratar o vazio? Por que isso muda a taxa geral?
3. Por que a função não pode mudar o `df` que recebeu?

## Tarefa 3. Ler um teste antes de rodar

Abra `tarefa3.py` e leia tudo antes de rodar. Anote na folha o que você acha que vai aparecer no terminal. Depois rode e compare.

1. Quais linhas aparecem antes de o programa parar? Qual o nome do erro?
2. O erro está na função ou no teste? Quando um mês não tem pedido nenhum, o que você quer que `taxa` retorne?
3. Reescreva a função e o terceiro teste para dizer isso. Rode de novo e anote a saída.

## Tarefa 4. A mesma regra em amostras diferentes

`tarefa4.py` lê os 2400 pedidos de `../dados/loja/pedidos.csv` e mede a regra "nunca cancela" em cinco amostras de 100 pedidos e em cinco amostras de 600. Rode e anote as três linhas.

1. A regra é a mesma nas dez contas. Por que os números mudam?
2. Por que as amostras de 100 variam mais que as de 600?
3. A gerente leu "83% contra 81%". Cada modelo foi medido numa amostra diferente de 100 pedidos. Dá para dizer qual é melhor? O que você pediria antes de responder?

## Tarefa 5. O mesmo modelo num mês diferente

Um modelo marca 60 de cada 100 pedidos que cancelam. Entre os pedidos que são entregues, ele marca 20 de cada 100 por engano.

1. Num mês de 1000 pedidos em que 200 cancelam, quantos pedidos ele marca? De cada 100 marcados, quantos cancelam?
2. Num mês de 1000 pedidos em que só 50 cancelam, faça as mesmas duas contas.
3. O modelo mudou de um mês para o outro? O que mudou?
4. No segundo mês, quanto acerta quem diz "não cancela" para todo pedido? Por que esse número não serve para escolher a regra?

## Depois das tarefas

Compare a folha com as respostas na aula e veja a tabela da apresentação do curso. Ela diz que aula de Python para dados ou de Estatística para decisão estudar para cada tarefa em que você travou.

Se precisar de ajuda, deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
