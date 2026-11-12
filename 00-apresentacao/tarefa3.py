def taxa(cancelados, pedidos):
    return round(100 * cancelados / pedidos, 1)


def testar():
    assert taxa(35, 110) == 31.8
    assert taxa(0, 50) == 0.0
    print("dois testes passaram")
    assert taxa(0, 0) == 0.0
    print("três testes passaram")


testar()
