# Plano de transformação: acompanhamento no primeiro mês

Base: `../dados/pessoas/admissoes.csv`, com as linhas do [contrato do alvo](../03-alvo-e-horizonte-da-previsao/contrato-alvo-admissoes.md) da aula 03. A conta de cada número está em `vazios_extremos.py`.

**Uso.** A lista do dia 7, para quem for contratado a partir de julho de 2026. O plano vale igual para o treino, a validação, o teste e cada pessoa nova.

**Onde o número é calculado.** No treino: as 787 admissões do contrato da aula 03 até 30/06/2025. A validação, o teste e as pessoas novas recebem os números prontos.

**Distância.** Vazia em 366 pessoas do treino. Em 358 delas, a admissão é de antes de 01/03/2025, quando o campo não existia. As outras 8 ficaram em branco. Tratamento: a mediana do treino, 5,2 km, sem indicador de vazio. Os extremos ficam: as 21 pessoas acima de 21,50 km são reais, e 57,1% delas saíram. Distância negativa ou acima de 100 km vira vazio e aviso.

**Salário.** Mais que o dobro ou menos que a metade da mediana do cargo no treino vira vazio e recebe essa mediana: atendimento 2300, caixa 2110, entregador 2420, estoque 2200, cargo sem treino 2210. No treino são as pessoas 440 e 396, que vão para o RH corrigir no cadastro. Na pessoa nova, a lista sai com o aviso "salário fora da faixa do cargo".

**Loja, cargo, turno e indicação.** Sem vazio no treino. Uma pessoa nova com uma delas vazia não recebe nota e vai para o aviso, porque o treino não ensinou o que fazer. Loja e cargo que o treino não tem ficam para a aula 08.

**Fora do modelo.** `data_desligamento` e `saiu_180d`: o vazio quer dizer que a saída ainda não aconteceu, e as duas montam o rótulo. `horas_treinamento`: nasce depois do dia 7, e os valores baixos vêm de quem já saiu.

**Aviso.** O plano volta para a mesa se, num mês, mais de 1 em cada 10 pessoas novas chegarem sem distância. Volta também se um campo de cadastro começar a vir vazio.

**Escrito em 8 de julho de 2026**, depois do contrato do alvo e do plano de validação, antes de treinar. Se o cadastro mudar ou a base for extraída de novo, eu escrevo outro.
