# ---------------------------------------------------------
# MODULOS/Anualidades.py
# Anualidades vencidas, anticipadas y perpetuas.
# Convenciones: i en porcentaje por período (5 = 5 %), n entero de períodos,
# A = cuota, P = valor presente, F = valor futuro. Las validaciones están en
# Validaciones/Validacion_anualidades.py. i = 0 no se admite (las fórmulas
# dividen entre i).
#
# Se usan log1p/expm1 para mantener la precisión con tasas muy pequeñas:
#   (1+i)^n - 1  =  expm1(n · log1p(i))
#   1 - (1+i)^-n = -expm1(-n · log1p(i))
# ---------------------------------------------------------

import math


# ---------------------------------------------------------
# FACTORES AUXILIARES (uso interno)
# ---------------------------------------------------------

def _factor_valor_presente(i_dec: float, n: float) -> float:
    """a_n = [1 - (1+i)^-n] / i : valor presente de 1 por período, vencida."""
    return -math.expm1(-n * math.log1p(i_dec)) / i_dec


def _factor_valor_futuro(i_dec: float, n: float) -> float:
    """s_n = [(1+i)^n - 1] / i : valor futuro de 1 por período, vencida."""
    return math.expm1(n * math.log1p(i_dec)) / i_dec


# ---------------------------------------------------------
# 1. ANUALIDADES PRESENTES VENCIDAS
# ---------------------------------------------------------

def valor_presente_anualidad_vencida(A: float, i: float, n: int) -> float:
    """P = A · a_n (cuotas al final de cada período)."""
    return A * _factor_valor_presente(i / 100, n)


def valor_anualidad_con_presente_vencida(P: float, i: float, n: int) -> float:
    """A = P / a_n: cuota que amortiza un presente P en n períodos."""
    return P / _factor_valor_presente(i / 100, n)


def valor_tiempo_anualidad_vencida_con_presente(P: float, i: float, A: float) -> float:
    """n = -ln(1 - P·i/A) / ln(1+i): períodos para amortizar P con cuota A."""
    i_dec = i / 100
    # log1p(-x) = ln(1 - x) con buena precisión.
    return -math.log1p(-(P * i_dec) / A) / math.log1p(i_dec)


# ---------------------------------------------------------
# 2. ANUALIDADES FUTURAS VENCIDAS
# ---------------------------------------------------------

def valor_futuro_anualidad_vencida(A: float, i: float, n: int) -> float:
    """F = A · s_n (cuotas al final de cada período)."""
    return A * _factor_valor_futuro(i / 100, n)


def valor_anualidad_con_futuro_vencida(F: float, i: float, n: int) -> float:
    """A = F / s_n: cuota necesaria para acumular F en n períodos."""
    return F / _factor_valor_futuro(i / 100, n)


def valor_tiempo_anualidad_vencida_con_futuro(F: float, i: float, A: float) -> float:
    """n = ln(1 + F·i/A) / ln(1+i): períodos para acumular F con cuota A."""
    i_dec = i / 100
    return math.log1p((F * i_dec) / A) / math.log1p(i_dec)


# ---------------------------------------------------------
# 3. ANUALIDADES ANTICIPADAS PRESENTES
# ---------------------------------------------------------

def valor_presente_anualidad_anticipada(A: float, i: float, n: int) -> float:
    """P = A · (1+i) · a_n  (equivale a A + A·a_{n-1}: primera cuota en t = 0)."""
    i_dec = i / 100
    return A * (1 + i_dec) * _factor_valor_presente(i_dec, n)


def valor_anualidad_con_presente_anticipada(P: float, i: float, n: int) -> float:
    """A = P / [(1+i) · a_n]: cuota anticipada que amortiza P en n períodos."""
    i_dec = i / 100
    return P / ((1 + i_dec) * _factor_valor_presente(i_dec, n))


def valor_tiempo_anualidad_anticipada_con_presente(P: float, i: float, A: float) -> float:
    """n = -ln(1 - P·i / [A(1+i)]) / ln(1+i)."""
    i_dec = i / 100
    return -math.log1p(-(P * i_dec) / (A * (1 + i_dec))) / math.log1p(i_dec)


# ---------------------------------------------------------
# 4. ANUALIDADES ANTICIPADAS FUTURAS
# ---------------------------------------------------------

def valor_futuro_anualidad_anticipada(A: float, i: float, n: int) -> float:
    """F = A · (1+i) · s_n  (equivale a A·[(1+i)^(n+1) - (1+i)] / i)."""
    i_dec = i / 100
    return A * (1 + i_dec) * _factor_valor_futuro(i_dec, n)


def valor_anualidad_con_futuro_anticipada(F: float, i: float, n: int) -> float:
    """A = F / [(1+i) · s_n]: cuota anticipada necesaria para acumular F."""
    i_dec = i / 100
    return F / ((1 + i_dec) * _factor_valor_futuro(i_dec, n))


def valor_tiempo_anualidad_anticipada_con_futuro(F: float, i: float, A: float) -> float:
    """n = ln(1 + F·i / [A(1+i)]) / ln(1+i)."""
    i_dec = i / 100
    return math.log1p((F * i_dec) / (A * (1 + i_dec))) / math.log1p(i_dec)


# ---------------------------------------------------------
# 5. ANUALIDADES PERPETUAS
# ---------------------------------------------------------

def anualidad_perpetua(A: float, i: float) -> float:
    """Valor presente de una perpetuidad vencida: P = A / i."""
    return A / (i / 100)