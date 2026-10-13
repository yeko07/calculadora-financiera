
# ---------------------------------------------------------
# VALIDACIONES/Validacion_interes_compuesto.py
# ---------------------------------------------------------

from Utilidades.ValidacionError import ValidacionError


def validar_valor_futuro(P, i, n):
    if P <= 0:
        raise ValidacionError(
            "El valor presente (P) debe ser un número positivo."
        )

    if i <= -100:
        raise ValidacionError(
            "La tasa periódica debe ser mayor que -100 %."
        )

    if n < 0:
        raise ValidacionError(
            "El número de períodos (n) no puede ser negativo."
        )


def validar_valor_presente(F, i, n):
    if F <= 0:
        raise ValidacionError(
            "El valor futuro (F) debe ser un número positivo."
        )

    if i <= -100:
        raise ValidacionError(
            "La tasa periódica debe ser mayor que -100 %."
        )

    if n < 0:
        raise ValidacionError(
            "El número de períodos (n) no puede ser negativo."
        )


def validar_valor_interes(F, P, n):
    if P <= 0:
        raise ValidacionError(
            "El valor presente (P) debe ser un número positivo."
        )

    if F <= 0:
        raise ValidacionError(
            "El valor futuro (F) debe ser un número positivo."
        )

    if F <= P:
        raise ValidacionError(
            "El valor futuro (F) debe ser mayor que el valor presente (P)."
        )

    if n <= 0:
        raise ValidacionError(
            "El número de períodos (n) debe ser mayor que cero."
        )


def validar_valor_periodo(F, P, i):
    if P <= 0:
        raise ValidacionError(
            "El valor presente (P) debe ser un número positivo."
        )

    if F <= 0:
        raise ValidacionError(
            "El valor futuro (F) debe ser un número positivo."
        )

    if F <= P:
        raise ValidacionError(
            "El valor futuro (F) debe ser mayor que el valor presente (P)."
        )

    if i <= 0:
        raise ValidacionError(
            "La tasa periódica debe ser mayor que cero para calcular "
            "un número finito de períodos."
        )
