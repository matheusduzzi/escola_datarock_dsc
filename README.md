# Kit do curso ML: preparação e validação

Os arquivos que você usa nas aulas: o diagnóstico, os pedidos da Loja Exemplo e a base de admissões do caso de pessoas.

## Como o kit está organizado

| Pasta | O que tem |
|---|---|
| `00-apresentacao/` | O [diagnóstico](00-apresentacao/diagnostico.md), os dados e programas das tarefas, a [folha de respostas](00-apresentacao/minhas-respostas.md), a folha da [ordem de estudo](00-apresentacao/minha-ordem.md) e a `primeira_olhada.py`, o programa da primeira seção da apresentação. |
| `dados/loja/` | 2400 pedidos da Loja Exemplo, com o rótulo de cancelamento. Ver [dados/loja/LEIA-ME.md](dados/loja/LEIA-ME.md). |
| `dados/pessoas/` | 1500 admissões da Loja Exemplo, com a saída antes de 180 dias. Ver [dados/pessoas/LEIA-ME.md](dados/pessoas/LEIA-ME.md). |
| `NN-titulo/` | Uma pasta por aula, com o número e o título da aula. Elas entram no kit junto com as aulas. |

Os comandos das aulas rodam de dentro da pasta da aula. Quando uma aula usa uma base compartilhada, ela diz o caminho, por exemplo `../dados/loja/pedidos.csv`.

## Do que você precisa

- Python 3.9 ou mais novo, com o pandas. É o ambiente de Python para dados; se você ainda não preparou o seu, a aula 38. Dependências e ambientes, de lá, mostra como.
- Um editor de código e um terminal.

O NumPy vem junto com o pandas. O scikit-learn entra na aula que usa o classificador pela primeira vez, com a versão, o Python mínimo e o comando de instalação.

Na pasta do kit, instale o que o diagnóstico usa:

```bash
python3 -m pip install -r requirements.txt
```

E veja se funcionou:

```bash
cd 00-apresentacao
python3 tarefa4.py
```

A saída tem três linhas. A primeira é `todos os 2400 pedidos: 0.805`; as outras duas são a tarefa 4 do diagnóstico. Se aparecer `No module named 'pandas'`, o `pip` instalou em outro Python. Rode `python3 -m pip install pandas` com o mesmo `python3` que você usa para rodar o programa. No Windows, troque `python3` por `py`.

Para gerar de novo as bases compartilhadas:

```bash
cd ../dados/loja
python3 gerar.py
cd ../pessoas
python3 gerar.py
```

As saídas são `pedidos=2400 cancelados=467 cancelados_com_entrega=22 entregues_com_dias_zero=0` e `pessoas=1500 com_rotulo=1210 saiu_180d=316 sem_rotulo=290 distancia_vazia=393 atendimento_digital=99 loja_L08=41`. Os dois geradores só usam a biblioteca padrão e saem iguais toda vez.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.

## Licença

A licença de uso e redistribuição do kit ainda vai ser definida pela Escola Datarock. Até lá, use os arquivos para estudar o curso. Os pedidos e as admissões da Loja Exemplo são inventados e foram gerados pelos programas do próprio kit.

## Aulas com arquivos neste kit

| Pasta | Aula |
|---|---|
| [00-apresentacao/](00-apresentacao/) | Apresentação |
| [02-tipos-de-aprendizado/](02-tipos-de-aprendizado/) | Tipos de aprendizado |
| [04-validacao-conforme-o-uso/](04-validacao-conforme-o-uso/) | Validação conforme o uso |
| [05-treino-validacao-e-teste/](05-treino-validacao-e-teste/) | Treino, validação e teste |
| [06-valores-vazios-e-extremos/](06-valores-vazios-e-extremos/) | Ausências e extremos |
| [07-scaling-e-distancias/](07-scaling-e-distancias/) | Scaling e distâncias |
| [09-pipeline-para-dados-de-pessoas/](09-pipeline-para-dados-de-pessoas/) | Pipeline de people analytics fictício |
| [11-baseline-e-metricas/](11-baseline-e-metricas/) | Baseline e métricas |
| [12-curvas-de-aprendizado/](12-curvas-de-aprendizado/) | Curvas de aprendizado |
| [13-desbalanceamento-e-prevalencia/](13-desbalanceamento-e-prevalencia/) | Desbalanceamento e prevalência |
| [14-comparar-estrategias/](14-comparar-estrategias/) | Comparar estratégias |
| [15-auditar-estabilidade-por-segmento/](15-auditar-estabilidade-por-segmento/) | Auditar estabilidade por segmento |
| [16-decidir-pelo-criterio/](16-decidir-pelo-criterio/) | Decidir pelo critério |
| [17-auditoria-de-um-pipeline/](17-auditoria-de-um-pipeline/) | Auditoria de um pipeline |
