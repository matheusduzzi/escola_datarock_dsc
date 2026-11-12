# 15. Auditar estabilidade por segmento

Os arquivos da aula «Auditar estabilidade por segmento» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `auditar.py` | O relatório da seção 3: quem cada recorte de loja, cargo e turno cobre, a lista em cada recorte com a faixa de 1000 sorteios e o melhor e o pior recorte com as notas embaralhadas |
| `segmentos.py` | As peças da auditoria: a faixa por sorteio com reposição, as quatro leituras e o embaralhamento das notas |
| `testar_segmentos.py` | Os testes do `segmentos.py` |
| `pipeline_pessoas.py` | O pipeline do acompanhamento, o mesmo `pipeline.py` da aula 09 |
| `pipeline_corrigido.py` | A preparação dos pedidos sem vazamento, a mesma da aula 10 |
| `classificador.py` | O classificador pronto (uma regressão logística) e o acerto do par, os mesmos da aula 10 |
| `auditoria_pedidos.py` | O exercício: a lista de ligações por categoria, pagamento e canal. Ele para com `NotImplementedError` até você escrever as três funções |
| `testar_auditoria_pedidos.py` | Os testes das três funções do exercício, com pedidos montados no próprio arquivo |
| `meu-relatorio.md` | A folha do exercício: a saída, a leitura e a resposta para a gerente |

As admissões vêm de `../dados/pessoas/admissoes.csv`: treino até 30/06/2025, validação de julho a setembro de 2025; o teste fica fechado. As pessoas novas são as admitidas depois de 01/01/2026. Os pedidos vêm de `../dados/loja/pedidos_export_completo.csv`: treino de janeiro a março de 2026, validação em abril e maio; junho é o teste e não entra em nenhuma conta. Rode de dentro dessa pasta:

```bash
python3 auditar.py
python3 auditar.py --colunas turno
python3 testar_segmentos.py
```

O primeiro dá a mesma saída toda vez, com o sorteio 15 escrito no `segmentos.py`. O segundo muda só o bloco 3: o embaralhamento olha só os recortes de turno.

O exercício:

```bash
python3 testar_auditoria_pedidos.py
python3 auditoria_pedidos.py
```

Antes de você escrever a `economia()`, a `por_recorte()` e a `embaralhar_recortes()`, os testes terminam com `FAILED (errors=8)` e código 1, e o `auditoria_pedidos.py` para com `NotImplementedError` depois das duas primeiras linhas. É o ponto de partida. Depois, os testes terminam com `OK`.

Tudo usa o pandas e o NumPy, que o README do kit já instala, e o `unittest`, que vem com o Python. Não precisa de internet nem do scikit-learn. Cada programa leva poucos segundos. Se você rodar de outra pasta, os programas param com uma mensagem que diz de onde rodar.

No Windows, troque `python3` por `py`.
