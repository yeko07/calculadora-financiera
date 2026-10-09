from Utilidades.ValidacionError import ValidacionError

def validar_valor_futuro(P, i, n):
    if P <= 0:
        raise ValidacionError("El valor presente (P) debe ser un número positivo.")
    if i < 0:
        raise ValidacionError("El valor del interés (i) no puede ser negativo.")
    if n < 0:
        raise ValidacionError("El número de periodos (n) no puede ser negativo.")

def validar_valor_presente(F, i, n):
    if F <= 0:
        raise ValidacionError("El valor futuro (F) debe ser un número positivo.")
    if i < 0:
        raise ValidacionError("El valor del interés (i) no puede ser negativo.")
    if n < 0:
        raise ValidacionError("El número de periodos (n) no puede ser negativo.")

def validar_valor_interes(F, P, n):
    if P <= 0:
        raise ValidacionError("El valor presente (P) debe ser un número positivo.")
    if F <= 0:
        raise ValidacionError("El valor futuro (F) debe ser un número positivo.")
    if F <= P:
        raise ValidacionError("El valor futuro (F) debe ser mayor que el valor presente (P).")
    if n <= 0:
        raise ValidacionError("El número de periodos (n) debe ser mayor a cero.")

def validar_valor_periodo(P, F, i):
    if P <= 0:
        raise ValidacionError("El valor presente (P) debe ser un número positivo.")
    if F <= 0:
        raise ValidacionError("El valor futuro (F) debe ser un número positivo.")
    if F <= P:
        raise ValidacionError("El valor futuro (F) debe ser mayor que el valor presente (P).")
    if i <= 0:
        raise ValidacionError("El valor del interés (i) debe ser mayor a cero.")

TIPOS_TASA_PERMITIDOS = ["Efectiva anual", "Periódica"]

def validar_periodicidad(tipo_tasa: str, periodicidad_tasa: str, periodicidad_periodo: str):
    # 1. si la tasa es efectiva anual el tiempo debe ser en años
    # 2. si el tiempo es años la tasa debe ser efectiva anual
    if tipo_tasa == "Efectiva anual" and periodicidad_periodo != "Años":
        raise ValidacionError(f"Inconsistencia: Ingresaste la tasa como efectiva anual pero el tiempo está en '{periodicidad_periodo}'."
                              " La periodicidad del tiempo y de la tasa deben ser equivalentes.")
    if periodicidad_periodo == "Años" and tipo_tasa != "Efectiva anual":
        raise ValidacionError(f"Inconsistencia: Ingresaste el tiempo en años pero la tasa está en '{tipo_tasa}'."
                              " La periodicidad del tiempo y de la tasa deben ser equivalentes.")
    # 3. si la tasa es periodica debe coincidir exactamente con el priodo del tiempo
    if tipo_tasa == "Periódica" and periodicidad_tasa != periodicidad_periodo:
        raise ValidacionError(f"Inconsistencia: La tasa es '{periodicidad_tasa}' pero el tiempo está en '{periodicidad_periodo}'. Ambos deben coincidir.")