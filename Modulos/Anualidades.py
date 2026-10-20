import math

# ====================================================================================================
# MÓDULOS ANUALIDADES
# =====================================================================================================


# -----------------------------------------------------------------------------------------------------
# 1. ANUALIDADES PRESENTES VENCIDAS
# ----------------------------------------------------------------------------------------------------

def valor_presente_anualidad_vencida(A: float, i: float, n: int) -> float:
    """Calcula el valor presente de una anualidad vencida"""
    i_dec = i / 100
    return A * (((1 + i_dec)**n - 1) / (i_dec * (1 + i_dec)**n))


def valor_anualidad_con_presente_vencida(P: float, i: float, n: int) -> float:
    """Calcula el valor de la anualidad vencida con el valor presente"""
    i_dec = i / 100
    return P * ((i_dec * (1 + i_dec)**n) / ((1 + i_dec)**n - 1))


def valor_tiempo_anualidad_vencida_con_presente(P: float, i: float, A: float) -> float:
    """Calcula el valor del tiempo de la anualidad vencida con el valor presente"""
    i_dec = i / 100
    return (-math.log(1 - ((P * i_dec) / A))) / math.log(1 + i_dec)


# ------------------------------------------------------------------------------------------------------
# 2. ANUALIDADES FUTURAS VENCIDAS
# ------------------------------------------------------------------------------------------------------

def valor_futuro_anualidad_vencida(A: float, i: float, n: int) -> float:
    """Calcula el valor futuro de la anualidad vencida"""
    i_dec = i / 100
    return A * (((1 + i_dec)**n - 1) / i_dec)


def valor_anualidad_con_futuro_vencida(F: float, i: float, n: int) -> float:
    """Calcula el valor de la anualidad vencida con el valor futuro"""
    i_dec = i / 100
    return F * (i_dec / ((1 + i_dec)**n - 1))


def valor_tiempo_anualidad_vencida_con_futuro(F: float, i: float, A: float) -> float:
    """Calcula el valor del tiempo de la anualidad vencida con el valor futuro"""
    i_dec = i / 100
    return math.log(((F * i_dec) / A) + 1) / math.log(1 + i_dec)


# -------------------------------------------------------------------------------------------------------
# 3. ANUALIDADES ANTICIPADAS PRESENTES
# -------------------------------------------------------------------------------------------------------

def valor_presente_anualidad_anticipada(A: float, i: float, n: int) -> float:
    """Calcula el valor presente de una anualidad anticipada"""
    i_dec = i / 100
    # CORREGIDO: Se agregó el operador * antes del paréntesis
    return A + A * (((1 + i_dec)**(n - 1) - 1) / (i_dec * (1 + i_dec)**(n - 1)))


def valor_anualidad_con_presente_anticipada(P: float, i: float, n: int) -> float:
    """Calcula el valor de la anualidad anticipada con el valor presente"""
    i_dec = i / 100
    return P / (1 + (((1 + i_dec)**(n - 1) - 1) / (i_dec * (1 + i_dec)**(n - 1))))


def valor_tiempo_anualidad_anticipada_con_presente(P: float, i: float, A: float) -> float:
    """Calcula el valor del tiempo de la anualidad anticipada con el valor presente"""
    i_dec = i / 100
    return (-math.log(1 - ((P * i_dec) / (A * (1 + i_dec))))) / math.log(1 + i_dec)


# -------------------------------------------------------------------------------------------------------
# 4. ANUALIDADES ANTICIPADAS FUTURAS
# -------------------------------------------------------------------------------------------------------

def valor_futuro_anualidad_anticipada(A: float, i: float, n: int) -> float:
    """Calcula el valor futuro de una anualidad anticipada"""
    i_dec = i / 100
    return A * (((1 + i_dec)**(n + 1) - (1 + i_dec)) / i_dec)


def valor_anualidad_con_futuro_anticipada(F: float, i: float, n: int) -> float:
    """Calcula el valor de la anualidad anticipada con el valor futuro"""
    i_dec = i / 100
    denominador = ((1 + i_dec)**(n + 1) - (1 + i_dec)) / i_dec
    return F / denominador


def valor_tiempo_anualidad_anticipada_con_futuro(F: float, i: float, A: float) -> float:
    """Calcula el valor del tiempo de la anualidad anticipada con el valor futuro"""
    i_dec = i / 100
    return math.log(((F * i_dec) / (A * (1 + i_dec))) + 1) / math.log(1 + i_dec)


# ----------------------------------------------------------------------------------------------------------
# 5. ANUALIDADES PERPETUAS
# ----------------------------------------------------------------------------------------------------------

def anualidad_perpetua(A: float, i: float) -> float:
    """Calcula el valor presente de una anualidad perpetua"""
    i_dec = i / 100
    return A / i_dec