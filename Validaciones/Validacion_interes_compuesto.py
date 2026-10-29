# ---------------------------------------------------------
# VALIDACIONES/Validacion_interes_compuesto.py
# Validaciones previas a las fórmulas de Modulos/Interes_compuesto.py.
# Política de tasas: se admiten tasas negativas (i > -100 %), por ejemplo
# para depreciación; i = -100 % anula el capital y no se permite.
# ---------------------------------------------------------

import math

from Utilidades.ValidacionError import ValidacionError
from Utilidades.Numeros import (
    LIMITE_EXPONENTE,
    exigir_numero,
    validar_sin_desbordamiento,
)

MSG_OBLIGATORIOS = "Todos los campos numéricos son obligatorios y deben ser números finitos."


def _validar_monto_positivo(valor: float, nombre: str) -> None:
    """Un monto (P o F) debe ser un número finito mayor que cero."""
    exigir_numero(valor, MSG_OBLIGATORIOS)
    if valor <= 0:
        raise ValidacionError(f"El valor {nombre} debe ser un número positivo.")


def _validar_tasa(i: float) -> None:
    """La tasa periódica debe ser un número finito mayor que -100 %."""
    exigir_numero(i, MSG_OBLIGATORIOS)
    if i <= -100:
        raise ValidacionError("La tasa periódica debe ser mayor que -100 %.")


def _validar_periodos_no_negativos(n: float) -> None:
    """Los períodos deben ser un número finito mayor o igual a cero."""
    exigir_numero(n, MSG_OBLIGATORIOS)
    if n < 0:
        raise ValidacionError("El número de períodos (n) no puede ser negativo.")


def _validar_periodos_positivos(n: float) -> None:
    """Los períodos deben ser un número finito mayor que cero."""
    exigir_numero(n, MSG_OBLIGATORIOS)
    if n <= 0:
        raise ValidacionError("El número de períodos (n) debe ser mayor que cero.")


# ---------------------------------------------------------
# VALOR FUTURO Y VALOR PRESENTE
# ---------------------------------------------------------

def validar_valor_futuro(P: float, i: float, n: float) -> None:
    """Valida P, i y n antes de calcular F = P(1+i)^n."""
    # Verifica cada dato por separado.
    _validar_monto_positivo(P, "presente (P)")
    _validar_tasa(i)
    _validar_periodos_no_negativos(n)
    # Evita OverflowError al elevar (1+i)^n.
    validar_sin_desbordamiento(i, n)


def validar_valor_presente(F: float, i: float, n: float) -> None:
    """Valida F, i y n antes de calcular P = F/(1+i)^n."""
    _validar_monto_positivo(F, "futuro (F)")
    _validar_tasa(i)
    _validar_periodos_no_negativos(n)
    # Evita desbordamiento y que (1+i)^n se anule (división por cero).
    validar_sin_desbordamiento(i, n)


# ---------------------------------------------------------
# TASA DE INTERÉS
# ---------------------------------------------------------

def validar_valor_interes(F: float, P: float, n: float) -> None:
    """Valida F, P y n antes de calcular i = (F/P)^(1/n) - 1.

    F puede ser menor, igual o mayor que P (tasa negativa, cero o positiva).
    """
    _validar_monto_positivo(P, "presente (P)")
    _validar_monto_positivo(F, "futuro (F)")
    _validar_periodos_positivos(n)

    # La raíz n-ésima de F/P debe ser representable: |ln(F/P)| / n acotado.
    if abs(math.log(F / P)) / n > LIMITE_EXPONENTE:
        raise ValidacionError(
            "La relación entre F, P y n produce una tasa demasiado grande "
            "para calcularse."
        )


# ---------------------------------------------------------
# NÚMERO DE PERÍODOS
# ---------------------------------------------------------

def validar_valor_periodo(F: float, P: float, i: float) -> None:
    """Valida F, P e i antes de calcular n = ln(F/P) / ln(1+i)."""
    _validar_monto_positivo(P, "presente (P)")
    _validar_monto_positivo(F, "futuro (F)")
    _validar_tasa(i)

    # Con i = 0 el capital nunca crece: n no existe (salvo F = P).
    if i == 0:
        raise ValidacionError(
            "La tasa periódica no puede ser cero para calcular el número "
            "de períodos."
        )

    # F > P exige i > 0 (crece) y F < P exige i < 0 (decrece).
    if (F > P and i < 0) or (F < P and i > 0):
        raise ValidacionError(
            "Con esa tasa el capital nunca llega a F: si F > P la tasa debe "
            "ser positiva y si F < P debe ser negativa."
        )