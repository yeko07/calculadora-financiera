# ---------------------------------------------------------
# VALIDACIONES/Validacion_anualidades.py
# Validaciones previas a las fórmulas de Modulos/Anualidades.py.
# Política: i debe ser finita, mayor que -100 % y distinta de cero.
# ---------------------------------------------------------

import math

from Utilidades.ValidacionError import ValidacionError
from Utilidades.Numeros import exigir_numero, validar_sin_desbordamiento


# ---------------------------------------------------------
# VALIDACIONES BÁSICAS
# ---------------------------------------------------------

def validar_monto(valor: float, nombre: str) -> None:
    """Valida que un valor monetario (A, P o F) sea finito y positivo."""
    exigir_numero(valor, f"El valor de {nombre} es obligatorio y debe ser un número finito.")
    if valor <= 0:
        raise ValidacionError(f"El valor de {nombre} debe ser un número positivo.")


def validar_tasa(i: float) -> None:
    """Valida la tasa periódica vencida: finita, > -100 % y distinta de cero."""
    exigir_numero(i, "La tasa de interés (i) es obligatoria y debe ser un número finito.")
    if i <= -100:
        raise ValidacionError("La tasa de interés (i) debe ser mayor que -100 %.")
    if i == 0:
        raise ValidacionError(
            "La tasa de interés (i) no puede ser cero en las anualidades "
            "(las fórmulas dividen entre i)."
        )


def validar_periodos_enteros(n: float) -> int:
    """Valida que n (ya en la periodicidad de cálculo) sea un entero positivo.

    Devuelve n como int. Protege contra truncamientos silenciosos: por
    ejemplo, 20 meses a trimestres da 6,67 y debe rechazarse.
    """
    exigir_numero(n, "El número de períodos (n) es obligatorio y debe ser un número finito.")

    # Redondea al entero más cercano y exige que n esté prácticamente en él.
    n_entero = round(n)
    if not math.isclose(n, n_entero, rel_tol=0, abs_tol=1e-6):
        raise ValidacionError(
            f"El tiempo equivale a {n:.4f} períodos de la periodicidad de "
            "cálculo y debe ser un número entero. Elige otra periodicidad "
            "de cálculo."
        )

    if n_entero <= 0:
        raise ValidacionError("El número de períodos (n) debe ser mayor a cero.")

    return int(n_entero)


def validar_tasa_y_periodos(i: float, n: int) -> None:
    """Valida la tasa y que n sea positivo, y que (1+i)^n sea calculable."""
    validar_tasa(i)
    exigir_numero(n, "El número de períodos (n) es obligatorio.")
    if n <= 0:
        raise ValidacionError("El número de períodos (n) debe ser mayor a cero.")
    # Evita OverflowError (o división por cero por subdesbordamiento).
    validar_sin_desbordamiento(i, n)


def validar_anualidad_con_periodos(
        monto: float, nombre_monto: str, i: float, n: float
) -> int:
    """Validación completa cuando n es dato: monto, tasa y n entero positivo."""
    validar_monto(monto, nombre_monto)
    n_entero = validar_periodos_enteros(n)
    validar_tasa_y_periodos(i, n_entero)
    return n_entero


# ---------------------------------------------------------
# VALIDACIONES PARA CALCULAR EL TIEMPO (n)
# ---------------------------------------------------------

def validar_calculo_tiempo_presente_vencida(P: float, i: float, A: float) -> None:
    """Valida P, i y A antes de n = -ln(1 - P·i/A) / ln(1+i)."""
    validar_monto(P, "el valor presente (P)")
    validar_monto(A, "la anualidad (A)")
    validar_tasa(i)

    # El argumento del logaritmo (1 - P·i/A) debe ser positivo.
    argumento = 1 - (P * (i / 100)) / A
    if argumento <= 0:
        raise ValidacionError(
            "La anualidad (A) no alcanza a cubrir los intereses del valor "
            "presente (P·i ≥ A), por lo que la deuda nunca se termina de pagar."
        )


def validar_calculo_tiempo_presente_anticipada(P: float, i: float, A: float) -> None:
    """Valida P, i y A antes de n = -ln(1 - P·i/[A(1+i)]) / ln(1+i)."""
    validar_monto(P, "el valor presente (P)")
    validar_monto(A, "la anualidad (A)")
    validar_tasa(i)

    i_dec = i / 100
    # El argumento del logaritmo debe ser positivo.
    argumento = 1 - (P * i_dec) / (A * (1 + i_dec))
    if argumento <= 0:
        raise ValidacionError(
            "La anualidad anticipada (A) no alcanza a cubrir los intereses "
            "del valor presente (P·i ≥ A·(1+i)), por lo que la deuda nunca "
            "se termina de pagar."
        )


def validar_calculo_tiempo_futuro(
        F: float, i: float, A: float, anticipada: bool = False
) -> None:
    """Valida F, i y A antes de calcular n con valor futuro.

    Con `anticipada=True` se usa la fórmula de anualidad anticipada. Con
    tasas negativas el argumento del logaritmo puede resultar ≤ 0, caso en
    el que la meta F es inalcanzable.
    """
    validar_monto(F, "el valor futuro (F)")
    validar_monto(A, "la anualidad (A)")
    validar_tasa(i)

    i_dec = i / 100
    # Cuota efectiva: A, o A(1+i) si es anticipada.
    cuota = A * (1 + i_dec) if anticipada else A

    # El argumento del logaritmo (1 + F·i/cuota) debe ser positivo.
    if 1 + (F * i_dec) / cuota <= 0:
        raise ValidacionError(
            "Con una tasa negativa y esa anualidad, el valor futuro (F) "
            "nunca puede alcanzarse."
        )


# ---------------------------------------------------------
# PERPETUIDADES
# ---------------------------------------------------------

def validar_calculo_perpetua(A: float, i: float) -> None:
    """Valida A e i de una perpetuidad (la tasa debe ser positiva)."""
    validar_monto(A, "la anualidad (A)")
    validar_tasa(i)
    if i < 0:
        raise ValidacionError(
            "En una anualidad perpetua la tasa debe ser positiva."
        )