# Escolha de escala do acompanhamento

Do curso ML: preparação e validação, aula «Scaling e distâncias». Os números saem do `escalas.py`, nessa pasta. Ela vem depois do [plano de transformação](../06-valores-vazios-e-extremos/plano-transformacao-admissoes.md) da aula 06.

**Modelo.** O modelo de vizinhos do Rafael: as 25 pessoas do treino mais perto, pela distância euclidiana, com salário, distância e indicação. Cargo e turno entram na aula 08, quando viram números.

**Escala.** Standard nas três colunas, calculada nas 787 pessoas do treino, depois do plano da aula 06. Salário: tira 2.244,24 e divide por 199,17. Distância: tira 6,34 e divide por 5,26. Indicação: tira 0,29 e divide por 0,46.

**O peso de cada coluna.** 33,3% para cada uma. Ninguém sabe ainda qual delas importa mais, e eu não quero que a unidade decida isso. Se o RH quiser dar mais peso à distância, isso entra aqui com o motivo e passa pela validação.

**Por que não as outras.** Sem escala, o salário é 99,9% da distância. Com o MinMax, a indicação é 76,7%, porque ela é 0 ou 1 e a distância fica espremida. Com o Robust, a distância é 97,5%, porque 370 das 787 pessoas têm 5,2 km depois do preenchimento e o divisor ficou em 1 km.

**O que a validação mostrou.** De 8 a 11 saídas entre as 36 maiores notas, e 7,8 numa lista sorteada. A diferença entre as escalas é de 3 pessoas, e ela não entra na escolha.

**A ordem.** Primeiro o plano da aula 06, depois a escala. Sem a correção do salário, o desvio padrão vai de 199,17 para 1.006,97 e o salário perde o peso.

**A pessoa nova.** Recebe os seis números prontos. Um salário de R$ 2.990 do atendimento digital vira 3,74 e entra assim, sem corte.

**Se o modelo for outro.** Árvore: sem escala, porque o corte separa as mesmas pessoas. Regressão logística do próximo curso: Standard, pela penalidade.

**Aviso.** A escolha volta para a mesa se uma coluna entrar ou sair do modelo. Volta também se o modelo mudar ou se o plano da aula 06 mudar o preenchimento.

**Escrito em 9 de julho de 2026**, um dia depois do plano de transformação, antes de treinar.
