# ---------------------------------------------------------
# UTILIDADES/Numeros.py
# Ayudas numéricas compartidas por todos los módulos de validación.
# ---------------------------------------------------------

import math
from typing import Any

from Utilidades.ValidacionError import ValidacionError

# Máximo exponente natural que admite un float de 64 bits: e^709 ≈ 8e307.
# Se usa 700 como margen de seguridad para evitar OverflowError.
LIMITE_EXPONENTE: float = 700.0


def es_numero_finito(valor: Any) -> bool:
    """True si `valor` es int/float (no bool) y no es NaN ni infinito."""
    return (
            isinstance(valor, (int, float))
            and not isinstance(valor, bool)
            and math.isfinite(valor)
    )


def exigir_numero(valor: Any, mensaje: str) -> None:
    """Lanza ValidacionError si `valor` es None, no numérico, NaN o infinito."""
    if valor is None or not es_numero_finito(valor):
        raise ValidacionError(mensaje)


def validar_sin_desbordamiento(i_porcentaje: float, n: float) -> None:
    """Verifica que (1 + i)^n sea representable (ni desborda ni se anula).

    Se evalúa con logaritmos: |n · ln(1 + i)| debe ser menor que el límite.
    Requiere i > -100 % (se valida antes de llamar a esta función).
    """
    exponente = n * math.log1p(i_porcentaje / 100)
    if abs(exponente) > LIMITE_EXPONENTE:
        raise ValidacionError(
            "La combinación de tasa y número de períodos es demasiado "
            "grande para calcularse. Reduce la tasa o los períodos."
        )