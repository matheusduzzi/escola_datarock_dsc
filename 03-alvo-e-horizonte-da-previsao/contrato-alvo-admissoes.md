# Contrato do alvo: acompanhamento no primeiro mês

O contrato da seção 6 da aula «Alvo e horizonte da previsão». Os números saem de `python3 rotulo.py`, nessa pasta.

**Pergunta.** No dia 7 depois da admissão, essa pessoa vai sair da Loja Exemplo até o dia 180?

**A linha.** Uma admissão. Na base, cada pessoa aparece uma vez. Entra quem ainda estava na loja no dia 7.

**Rótulo.** 1 se `data_desligamento` cai até 180 dias depois de `data_admissao`, contando o dia 180. 0 se a pessoa completou 180 dias sem sair. Qualquer motivo de saída conta.

**Horizonte e maturação.** 180 dias. Com a base extraída em 30/06/2026, entram as admissões até 01/01/2026. As de depois ficam fora do treino e de toda taxa, mesmo quem já saiu.

**Colunas que entram.** `data_admissao` (só para separar por tempo), `loja`, `cargo`, `turno`, `salario_base`, `distancia_km`, `indicacao`.

**Colunas que ficam fora.** `data_desligamento`: monta o rótulo. `saiu_180d`: é o rótulo. `horas_treinamento`: é a soma do primeiro mês e ainda não fechou no dia 7.

**Números da base.** 1169 pessoas, 275 saíram, 23,5%. O rótulo refeito pelas datas bate com `saiu_180d` nas 1500 linhas.

**Escrito em 6 de julho de 2026**, antes de treinar qualquer modelo. Se o horizonte, o dia da lista ou a data da extração mudarem, eu escrevo outro contrato.

## Casos de fronteira

Linhas reais de `../dados/pessoas/admissoes.csv`.

| Pessoa | Admissão | Saída | Dias até sair | Rótulo | No treino? |
|---|---|---|---|---|---|
| 787 | 13/07/2024 | 20/07/2024 | 7 | 1 | Fora: saiu no dia 7, a lista chega tarde |
| 947 | 26/12/2024 | 24/06/2025 | 180 | 1 | Entra: o dia 180 ainda conta |
| 67 | 07/02/2025 | 10/08/2025 | 184 | 0 | Entra como 0: saiu depois do horizonte |
| 1447 | 01/01/2026 | ainda na loja | | 0 | Entra: completou 180 dias no dia da extração |
| 716 | 02/01/2026 | ainda na loja | | vazio | Fora: falta um dia para ter resposta |
| 752 | 02/01/2026 | 19/03/2026 | 76 | 1 | Fora: a turma dela ainda não tem resposta |
