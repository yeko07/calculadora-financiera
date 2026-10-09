import math

def valor_futuro(P: float, i_porcentaje: float, n: float) -> float:
    # Convertimos la tasa recibida (%) a decimal
    i = i_porcentaje / 100.0
    F = P * ((1 + i) ** n)
    return F

def valor_presente(F: float, i_porcentaje: float, n: float) -> float:
    # Convertimos la tasa recibida (%) a decimal
    i = i_porcentaje / 100.0
    P = F / ((1 + i) ** n)
    return P

def valor_interes(F: float, P: float, n: float) -> float:
    # Calculamos la tasa en decimal
    i_decimal = ((F / P) ** (1 / n)) - 1
    # Devolvemos la tasa expresada en porcentaje (%) para la UI
    return i_decimal * 100.0

def valor_periodo(F: float, P: float, i_porcentaje: float) -> float:
    # Convertimos la tasa recibida (%) a decimal
    i = i_porcentaje / 100.0
    n = math.log(F / P) / math.log(1 + i)
    return n