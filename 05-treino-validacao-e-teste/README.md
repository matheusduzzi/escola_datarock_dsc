# 05. Treino, validação e teste

Os arquivos da aula «Treino, validação e teste» do curso ML: preparação e validação.

| Arquivo | Para quê |
|---|---|
| `particoes.py` | Divide os pedidos pela data em treino, validação e teste, grava `particoes.csv` e `manifesto.txt` e, com `--checar`, compara um arquivo de partes com a regra e com o manifesto |
| `escolher.py` | Ajusta cinco regras de ligação no treino, mede na validação e escolhe uma pela regra escrita no próprio programa. Não faz conta com o teste |
| `minhas-particoes.md` | A folha do exercício: treino, validação e teste das admissões |

Os dois programas leem a base compartilhada do kit, em `../dados/loja/pedidos.csv`. Rode de dentro dessa pasta, nessa ordem:

```bash
python3 particoes.py
python3 particoes.py --checar particoes.csv
python3 escolher.py
```

O `escolher.py` roda a mesma checagem antes de começar. Se `particoes.csv` ou a base mudarem depois do `manifesto.txt`, ele para e manda rodar o `--checar`, que mostra o que não bate. Para começar do zero, rode `python3 particoes.py` de novo: ele grava as duas coisas outra vez.

Eles usam o pandas, que o README do kit já instala. Não precisam de internet.

O exercício usa `../dados/pessoas/admissoes.csv`. Você escreve o seu próprio código no pandas; pode partir do `particoes.py`.

No Windows, troque `python3` por `py`.
