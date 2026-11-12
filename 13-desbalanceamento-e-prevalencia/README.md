# 13. Desbalanceamento e prevalência

Os arquivos da aula «Desbalanceamento e prevalência» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `reamostragem.py` | As contas da aula: aplica peso, subamostragem, sobreamostragem e SMOTE no treino dos pedidos, mede na validação como ela chegou, corrige a escala das notas, compara reamostrar dentro e fora das dobras e mede a validação reamostrada |
| `pipeline_corrigido.py` | A preparação corrigida da aula 10, sem mudança: divide pelas datas da aula 05 e ajusta tudo só no treino |
| `classificador.py` | O classificador pronto da aula 10, sem mudança |
| `plano-desbalanceamento-pedidos.md` | O plano de desbalanceamento do cancelamento, da seção 7 |
| `meu-plano.md` | A folha do exercício: o plano de desbalanceamento do acompanhamento |

O `reamostragem.py` lê a base compartilhada do kit, em `../dados/loja/pedidos_export_completo.csv`. Junho, o teste, sai logo na leitura e não entra em nenhuma conta. Rode de dentro dessa pasta:

```bash
python3 reamostragem.py
python3 reamostragem.py --proporcao 0.33
python3 reamostragem.py --prevalencia 0.30
```

`--proporcao` diz a parte de cancelados que o treino passa a ter depois da estratégia. O padrão é 0.5, e o programa aceita de 0.25 a 0.5. `--prevalencia` acrescenta o bloco 6: a mesma validação pesada para outra parte de cancelados, de 0.05 a 0.6. Fora dessas faixas, o programa para com uma mensagem de erro. Os sorteios são fixos, então a saída é a mesma toda vez. Ela leva uns segundos.

O SMOTE e a sobreamostragem estão escritos no próprio `reamostragem.py`, com o NumPy, em poucas linhas cada. Assim dá para ler o que cada estratégia faz, e a aula não precisa de biblioteca nova. Em projeto, a biblioteca imbalanced-learn tem as mesmas estratégias e o `Pipeline` que reamostra só no treino.

Ele usa o pandas, que o README do kit já instala. Não precisa de internet nem do scikit-learn.

O exercício usa `../dados/pessoas/admissoes.csv`, o contrato do alvo que você escreveu na aula 03 e as datas da aula 09. Você escreve o seu próprio código no pandas.

No Windows, troque `python3` por `py`.
