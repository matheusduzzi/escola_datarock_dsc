# 04. Validação conforme o uso

Os arquivos da aula «Validação conforme o uso» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `dobras.py` | A conta da seção 3: testa a regra "taxa de saída do cargo" por seis jeitos de separar as admissões e compara as saídas esperadas com as reais em cada parte de teste |
| `plano-validacao-admissoes.md` | O plano de validação do acompanhamento, da seção 6 |
| `meu-plano.md` | A folha do exercício: o plano de validação do modelo de cancelamento |

O `dobras.py` lê a base compartilhada do kit, em `../dados/pessoas/admissoes.csv`, e usa as linhas do contrato da aula 03. Rode de dentro dessa pasta:

```bash
python3 dobras.py
python3 dobras.py --dobras 10
python3 dobras.py --sem-intervalo
```

O padrão é 5 dobras. `--dobras` aceita de 2 a 50; fora disso o programa para com uma mensagem de erro. `--sem-intervalo` muda só o bloco 5: o treino passa a ter tudo o que veio antes do trimestre de teste. O sorteio das dobras é fixo, então a saída é a mesma toda vez.

Ele usa o pandas, que o README do kit já instala. Não precisa de internet nem do scikit-learn.

O exercício usa `../dados/loja/pedidos_export_completo.csv` e o contrato do rótulo que você escreveu na aula 03. Você escreve o seu próprio código no pandas.

No Windows, troque `python3` por `py`.
