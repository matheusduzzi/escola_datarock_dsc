# Mapa de transformação das categorias: admissões

O mapa da seção 6 da aula «Encoding de categorias». Ele completa o [plano de transformação](../06-valores-vazios-e-extremos/plano-transformacao-admissoes.md) da aula 06 e usa o [contrato do alvo](../03-alvo-e-horizonte-da-previsao/contrato-alvo-admissoes.md) da aula 03. Os números saem do `encoding.py`, nessa mesma pasta.

**Uso.** A lista do dia 7, para quem for contratado a partir de julho de 2026. O mapa vale igual para o treino, a validação, o teste e cada pessoa nova.

**Onde o número é calculado.** No treino: as 787 admissões até 30/06/2025. As 188 pessoas do teste ficaram fechadas. Nenhum número do mapa usa elas.

**Loja.** One-hot com as 7 colunas do treino, de L01 a L07. A L08 fica com as 7 zeradas, recebe nota e sai na lista com o aviso "loja que o treino não tem". Ela é medida à parte quando as respostas chegarem.

**Cargo.** One-hot com as 4 colunas do treino. O atendimento digital fica com as 4 zeradas e sai com o aviso "cargo que o treino não tem". O menor cargo tem 165 pessoas no treino, e o one-hot dá conta sem usar a resposta.

**Turno.** One-hot com as 3 colunas do treino. Não vai como ordinal: a saída não segue a ordem do dia (manhã 27,0%, tarde 20,3%, noite 32,9%).

**Indicação.** Já é 0 e 1. Fica como está.

**Equipe.** Fora do modelo. Fora da dobra, a nota da equipe acerta 53,7% dos pares no treino, e 53,2% na validação. Se um dia entrar, entra por target encoding fora da dobra, com 5 dobras no treino e suavização de 20 pessoas. Equipe que o treino não tem recebe 25,8%, a taxa do treino.

**Aviso.** O mapa volta para a mesa quando chega uma categoria que o treino não tem. Volta também quando mais de 1 em cada 10 pessoas novas chegam numa delas. Hoje são 94 de 325: o próximo treino precisa da L08 e do atendimento digital, assim que essas pessoas tiverem resposta.

**Escrito em 9 de julho de 2026**, depois do plano de transformação da aula 06, antes de treinar. Se o cadastro ganhar uma categoria ou a base for extraída de novo, eu escrevo outro.

## As colunas que a pessoa nova recebe

As 14 colunas do treino, nessa ordem. Uma pessoa nova ganha exatamente essas colunas, com 1 na da categoria dela e 0 nas outras. Categoria que o treino não tem deixa as colunas daquela coluna zeradas e vai para o aviso.

| Coluna de origem | Colunas do one-hot |
|---|---|
| `loja` | `loja_L01`, `loja_L02`, `loja_L03`, `loja_L04`, `loja_L05`, `loja_L06`, `loja_L07` |
| `cargo` | `cargo_atendimento`, `cargo_caixa`, `cargo_entregador`, `cargo_estoque` |
| `turno` | `turno_manha`, `turno_noite`, `turno_tarde` |
