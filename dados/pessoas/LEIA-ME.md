# Admissões da Loja Exemplo

O RH da Loja Exemplo quer oferecer acompanhamento no primeiro mês para quem tem mais chance de sair antes de 180 dias. As pessoas são inventadas: `gerar.py` sorteia cada linha com a biblioteca padrão do Python. Nenhum dado vem de pessoa ou empresa real. O modelo do curso nunca decide quem é contratado.

## Arquivo

`admissoes.csv` tem 1500 linhas. Uma linha é uma pessoa contratada entre 2024-07-01 e 2026-05-31. A base foi extraída em 2026-06-30.

| Coluna | O que é |
|---|---|
| `id_pessoa` | número da pessoa na base |
| `data_admissao` | dia da contratação |
| `loja` | `L01` a `L08` |
| `cargo` | caixa, estoque, atendimento, entregador ou atendimento digital |
| `turno` | manha, tarde ou noite |
| `salario_base` | salário de contratação, em reais |
| `distancia_km` | distância de casa até a loja; às vezes vazia |
| `indicacao` | 1 quando a pessoa veio por indicação |
| `horas_treinamento` | horas de treinamento no primeiro mês |
| `data_desligamento` | dia da saída; vazia se a pessoa continuava na empresa na extração |
| `saiu_180d` | 1 se saiu até 180 dias depois da admissão, 0 se passou dos 180 dias, vazio nos outros casos |

## Como gerar de novo

```bash
python3 gerar.py
```

A saída é `pessoas=1500 com_rotulo=1210 saiu_180d=316 sem_rotulo=290 distancia_vazia=393 atendimento_digital=99 loja_L08=41`. O arquivo sai igual toda vez. Nas aulas, você prepara e avalia primeiro e só depois abre o gerador para comparar.

Não edite o CSV à mão.
