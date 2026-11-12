import pandas as pd

pedidos = pd.read_csv("../dados/loja/pedidos.csv")

# A regra "nunca cancela" acerta todo pedido que não foi cancelado.
acerto = pedidos["cancelado"] == 0
print("todos os 2400 pedidos:", round(float(acerto.mean()), 3))

for tamanho in (100, 600):
    taxas = [round(float(acerto.sample(tamanho, random_state=s).mean()), 3) for s in range(1, 6)]
    print(tamanho, "pedidos por amostra:", taxas, "| maior menos menor:", round(max(taxas) - min(taxas), 3))
