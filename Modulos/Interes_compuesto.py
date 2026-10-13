
# ---------------------------------------------------------
# MODULOS/Interes_compuesto.py
# ---------------------------------------------------------

import math


def valor_futuro(p: float, i_porcentaje: float, n: float) -> float:
    """Calcula el valor futuro a partir del valor presente."""
    i = i_porcentaje / 100
    return p * ((1 + i) ** n)


def valor_presente(f: float, i_porcentaje: float, n: float) -> float:
    """Calcula el valor presente a partir del valor futuro."""
    i = i_porcentaje / 100
    return f / ((1 + i) ** n)


def valor_interes(f: float, p: float, n: float) -> float:
    """Calcula la tasa periódica necesaria para pasar de P a F."""
    i_decimal = ((f / p) ** (1 / n)) - 1
    return i_decimal * 100


def valor_periodo(f: float, p: float, i_porcentaje: float) -> float:
    """Calcula la cantidad de períodos necesarios para pasar de P a F."""
    i = i_porcentaje / 100
    return math.log(f / p) / math.log(1 + i)
