# ---------------------------------------------------------
# VALIDACIONES/Validacion_anualidades.py
# ---------------------------------------------------------

from Utilidades.ValidacionError import ValidacionError


def validar_tasa_y_periodos(i: float, n: int) -> None:
    """Valida que la tasa no sea cero y que los períodos sean mayores a cero."""
    if i == 0:
        raise ValidacionError("La tasa de interés (i) no puede ser cero.")
    if n <= 0:
        raise ValidacionError("El número de períodos (n) debe ser mayor a cero.")


def validar_tasa(i: float) -> None:
    """Valida que la tasa de interés no sea cero (para perpetuidades)."""
    if i == 0:
        raise ValidacionError("La tasa de interés (i) no puede ser cero en anualidades perpetuas.")


def validar_calculo_tiempo_presente_vencida(P: float, i: float, A: float) -> None:
    """Valida los parámetros antes de calcular el tiempo (n) con Valor Presente (vencida)."""
    validar_tasa(i)
    if A == 0:
        raise ValidacionError("El pago de la anualidad (A) no puede ser cero.")

    i_dec = i / 100
    # Evitar dominio negativo o cero en el logaritmo: 1 - ((P * i_dec) / A) > 0
    argumento = 1 - ((P * i_dec) / A)
    if argumento <= 0:
        raise ValidacionError("Los datos ingresados generan una indeterminación matemática (logaritmo de un número menor o igual a cero). Verifique los valores.")


def validar_calculo_tiempo_presente_anticipada(P: float, i: float, A: float) -> None:
    """Valida los parámetros antes de calcular el tiempo (n) con Valor Presente (anticipada)."""
    validar_tasa(i)
    if A == 0:
        raise ValidacionError("El pago de la anualidad (A) no puede ser cero.")

    i_dec = i / 100
    denominador = A * (1 + i_dec)
    if denominador == 0:
        raise ValidacionError("El denominador de la fórmula no puede ser cero.")

    argumento = 1 - ((P * i_dec) / denominador)
    if argumento <= 0:
        raise ValidacionError("Los datos ingresados generan un logaritmo no válido para anualidades anticipadas.")


def validar_calculo_tiempo_futuro(A: float, i: float) -> None:
    """Valida los parámetros generales para cálculos de tiempo con Valor Futuro."""
    validar_tasa(i)
    if A == 0:
        raise ValidacionError("El pago de la anualidad (A) no puede ser cero.")