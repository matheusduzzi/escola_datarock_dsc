import pandas as pd

export = pd.read_csv("../dados/loja/pedidos_export_completo.csv")
pedidos = pd.read_csv("../dados/loja/pedidos.csv")
cancelou = export["cancelado"] == 1


def pct(a, b):
    return f"{100 * a / b:.1f}".replace(".", ",") + "%"


print("1. A regra do export: cancela se a entrega levou zero dia")
zero = export["dias_ate_entrega"] == 0
acertos = int((zero == cancelou).sum())
print(f"   acerta {acertos} de {len(export)} pedidos ({pct(acertos, len(export))})")

print("2. Quando o zero aparece")
print(f"   cancelados: {int((zero & cancelou).sum())} com zero dia, {int((~zero & cancelou).sum())} com mais de zero")
print(f"   entregues: {int((zero & ~cancelou).sum())} com zero dia")
novas = sorted(set(export.columns) - set(pedidos.columns))
print(f"   colunas do export que pedidos.csv não tem: {', '.join(novas)}")

print("3. Duas regras que dá para usar antes do despacho")
cancelados = int(cancelou.sum())
entregues = len(pedidos) - cancelados
print(f"   nunca cancela: acerta {entregues} de {len(pedidos)} ({pct(entregues, len(pedidos))}), liga para ninguém")
boleto = pedidos["forma_pagamento"] == "boleto"
certos = int((boleto & (pedidos["cancelado"] == 1)).sum())
acerto_boleto = int((boleto == (pedidos["cancelado"] == 1)).sum())
print(f"   boleto: acerta {acerto_boleto} de {len(pedidos)} ({pct(acerto_boleto, len(pedidos))})")
print(f"   boleto: liga para {int(boleto.sum())}, {certos} iam cancelar ({pct(certos, int(boleto.sum()))} das ligações)")
print(f"   boleto: pega {certos} de {cancelados} cancelamentos ({pct(certos, cancelados)})")

print("4. A mesma regra em meses que ela não viu")
mes = pedidos["data_pedido"].str[:7]
for nome, parte in [("jan a abr", mes <= "2026-04"), ("mai e jun", mes >= "2026-05")]:
    q = pedidos[parte]
    b = q["forma_pagamento"] == "boleto"
    c = int((b & (q["cancelado"] == 1)).sum())
    print(f"   {nome}: {int(parte.sum())} pedidos, {c} de {int(b.sum())} ligações iam cancelar ({pct(c, int(b.sum()))})")
