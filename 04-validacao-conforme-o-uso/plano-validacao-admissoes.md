# Plano de validação do acompanhamento

O plano da seção 6 da aula «Validação conforme o uso». Pergunta do modelo e base: o contrato do alvo da aula 03, em `../03-alvo-e-horizonte-da-previsao/contrato-alvo-admissoes.md`.

> **Uso.** Em julho de 2026, o modelo treina com as 1169 admissões do contrato da aula 03. A lista sai no dia 7 de cada pessoa contratada daí em diante, nas oito lojas e nos cinco cargos.
>
> **Separação principal: por tempo, com intervalo.** Três testes, um por trimestre: 2025-T2, 2025-T3 e 2025-T4. O treino de cada um tem só quem entrou até 180 dias antes do primeiro dia do trimestre: até 03/10/2024, 02/01/2025 e 04/04/2025. O resultado sai por trimestre.
>
> **Teste a mais: uma loja fora.** As lojas L01 a L07 saem do treino uma de cada vez. A L08 tem uma pessoa com resposta: entra no treino e não vira teste. As primeiras respostas dela chegam em julho de 2026, e eu meço a L08 à parte quando elas chegarem.
>
> **Proporção.** Sem estratificar. Cada trimestre de teste fica com a taxa que teve: 23,9%, 21,6% e 16,3%.
>
> **Cargo novo.** O atendimento digital começou em outubro de 2025, e nenhum treino dos três testes tem esse cargo. O resultado dele sai separado.
>
> **Fora do plano.** Holdout aleatório, k-fold aleatório ou estratificado e leave-one-out. Os quatro misturam 2024 e 2025 no treino e no teste e ensaiam uma taxa de 23,5% que o último trimestre não teve. Com a regra do cargo, o k-fold estratificado errou no máximo 1,6 saída por dobra. O teste por tempo errou 21,1 no último trimestre.
>
> **Escrito em 7 de julho de 2026**, antes de treinar o modelo. Se a lista mudar de população ou de dia, ou se a base for extraída de novo, eu escrevo outro plano.

Os números do plano saem de `python3 dobras.py`, rodado nessa pasta.
