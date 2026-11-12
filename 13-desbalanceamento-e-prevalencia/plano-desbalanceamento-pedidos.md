# Plano de desbalanceamento: cancelamento antes do despacho

O plano da aula «Desbalanceamento e prevalência», seção 7. Ele vem depois do briefing da aula 01, da divisão da aula 05 e da preparação da aula 10, e vale para o modelo de cancelamento dos pedidos.

**Uso.** A lista de ligações roda em todos os pedidos de julho de 2026, na hora do pedido, antes do despacho. A mistura de julho ninguém sabe. Abril e maio tiveram 20,5% de cancelados.

**Teste.** Os 450 pedidos de junho, como chegaram, medidos uma vez na aula 16 com a régua do briefing. Sem SMOTE, sem cópia, sem tirar pedido, sem peso e sem estratificar. Ninguém conta os cancelados de junho antes disso.

**Validação.** Os 795 pedidos de abril e maio, também como chegaram. Toda candidata é medida neles, nos mesmos pedidos.

**Candidatas.** Nada, peso, subamostragem, sobreamostragem e SMOTE, todas levando o treino de janeiro a março a 50% de cancelados. O SMOTE fica marcado: 406 dos 697 pedidos inventados têm categoria, pagamento ou canal pela metade.

**Onde entram.** Depois da divisão da aula 05 e da preparação da aula 10, ajustada só no treino. A estratégia mexe só nos 1155 pedidos de janeiro a março. Se alguém usar dobras dentro do treino, a reamostragem entra dentro de cada dobra.

**Escala.** O fator é 4,04 para as quatro. Antes de qualquer lista, a nota é corrigida, ou o corte sobe de 0,333 para 0,669. Sem a correção, as quatro listas não cabem na equipe.

**Relatório.** Para cada candidata, na validação: o acerto do par, as ligações, a precisão, a revocação e o custo no corte corrigido. As que sorteiam rodam com vários sorteios, e o relatório mostra a faixa. Uma candidata só substitui o modelo sem estratégia se ganhar dele fora dessa faixa.

**Escrito em 13 de julho de 2026**, antes de medir as candidatas com vários sorteios. Se a mistura de julho mudar muito, ou se a base for extraída de novo, eu escrevo outro plano.

## De onde vêm os números

- 1155 pedidos de janeiro a março, 229 cancelados; 795 de abril e maio, 163 cancelados (20,5%): `python3 reamostragem.py`, cabeçalho. Os 450 de junho vêm da divisão da aula 05.
- 697 pedidos inventados, 406 com categoria, pagamento ou canal pela metade; fator 4,04: bloco 1.
- Corte equivalente 0,669 e as listas que não cabem sem a correção: blocos 2 e 3.
- Reamostragem dentro de cada dobra: bloco 4.
