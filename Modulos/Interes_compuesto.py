# ---------------------------------------------------------
# MODULOS/Interes_compuesto.py
# Fórmulas de interés compuesto. Todas las tasas se reciben y devuelven
# en porcentaje por período (5 significa 5 %). La validación de los datos
# vive en Validaciones/Validacion_interes_compuesto.py.
# ---------------------------------------------------------

import math


def valor_futuro(p: float, i_porcentaje: float, n: float) -> float:
    """Valor futuro: F = P · (1 + i)^n."""
    # Pasa la tasa de porcentaje a decimal.
    i = i_porcentaje / 100
    # Capitaliza el valor presente durante n períodos.
    return p * ((1 + i) ** n)


def valor_presente(f: float, i_porcentaje: float, n: float) -> float:
    """Valor presente: P = F / (1 + i)^n."""
    # Pasa la tasa de porcentaje a decimal.
    i = i_porcentaje / 100
    # Descuenta el valor futuro n períodos.
    return f / ((1 + i) ** n)


def valor_interes(f: float, p: float, n: float) -> float:
    """Tasa periódica (en %) que lleva P a F en n períodos: i = (F/P)^(1/n) - 1."""
    # Raíz n-ésima de la razón F/P, menos 1, da la tasa decimal.
    i_decimal = ((f / p) ** (1 / n)) - 1
    # Se devuelve en porcentaje.
    return i_decimal * 100


def valor_periodo(f: float, p: float, i_porcentaje: float) -> float:
    """Número de períodos para pasar de P a F: n = ln(F/P) / ln(1 + i)."""
    # Pasa la tasa de porcentaje a decimal.
    i = i_porcentaje / 100
    # log1p(i) = ln(1 + i) con mejor precisión cuando i es pequeña.
    return math.log(f / p) / math.log1p(i)