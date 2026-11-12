# 12. Curvas de aprendizado

Os arquivos da aula «Curvas de aprendizado» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `curva.py` | As curvas de aprendizado de três modelos, de onde vem a distância entre treino e validação e quanto a validação varia. Sem opção, nos pedidos; com `--caso pessoas`, nas admissões do exercício |
| `meses.py` | A prática guiada, pedido 3: três treinos diferentes medidos nos pedidos de maio |
| `pipeline_corrigido.py` | A preparação dos pedidos sem vazamento, a mesma da aula 10 |
| `pipeline_pessoas.py` | O pipeline do acompanhamento, o mesmo `pipeline.py` da aula 09 |
| `classificador.py` | O classificador pronto (uma regressão logística) e o acerto do par, os mesmos da aula 10 |
| `minhas-hipoteses.md` | A folha do exercício: o diagnóstico de cada modelo, as hipóteses e a recomendação para a Marta |

Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv` e as admissões de `../dados/pessoas/admissoes.csv`. Pedidos: treino de janeiro a março de 2026, validação em abril e maio; junho é o teste e não entra em nenhuma conta. Admissões: treino até 30/06/2025, validação de julho a setembro de 2025; o teste fica fechado. Rode de dentro dessa pasta:

```bash
python3 curva.py
python3 meses.py
python3 curva.py --caso pessoas
```

Os três dão a mesma saída toda vez. O `curva.py` leva uns segundos nos pedidos e um pouco mais nas admissões, porque treina o mesmo modelo muitas vezes.

Tudo usa o pandas e o NumPy, que o README do kit já instala. Não precisa de internet nem do scikit-learn. Se você rodar de outra pasta, o `curva.py` para com uma mensagem que diz de onde rodar.

No Windows, troque `python3` por `py`.
