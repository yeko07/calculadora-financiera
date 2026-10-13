
# ---------------------------------------------------------
# VALIDACIONES/Validacion_conversiones.py
# ---------------------------------------------------------

from Utilidades.ValidacionError import ValidacionError
from Modulos.Conversiones import PERIODOS_ANUALES


def validar_periodicidad(periodicidad):
    if periodicidad not in PERIODOS_ANUALES:
        raise ValidacionError(
            f"La periodicidad '{periodicidad}' no es válida."
        )


def validar_frecuencia(m):
    if m <= 0:
        raise ValidacionError(
            "La frecuencia de capitalización debe ser mayor que cero."
        )


def validar_tasa_no_negativa(tasa):
    if tasa < 0:
        raise ValidacionError("La tasa de interés no puede ser negativa.")


def validar_tasa_mayor_menos_100(tasa):
    if tasa <= -100:
        raise ValidacionError("La tasa debe ser mayor que -100 %.")


# ---------------------------------------------------------
# TASA PERIODICA Y NOMINAL
# ---------------------------------------------------------

def validar_periodica_nominal(i_p, m):
    validar_tasa_no_negativa(i_p)
    validar_frecuencia(m)


def validar_nominal_periodica(i_n, m):
    validar_tasa_no_negativa(i_n)
    validar_frecuencia(m)


# ---------------------------------------------------------
# TASA NOMINAL Y EFECTIVA ANUAL
# ---------------------------------------------------------

def validar_nominal_efectiva(i_n, m):
    validar_tasa_no_negativa(i_n)
    validar_frecuencia(m)


def validar_efectiva_nominal(i_ea, m):
    validar_tasa_mayor_menos_100(i_ea)
    validar_frecuencia(m)


# ---------------------------------------------------------
# TASA EFECTIVA ANUAL Y PERIODICA
# ---------------------------------------------------------

def validar_efectiva_periodica(i_ea, m):
    validar_tasa_mayor_menos_100(i_ea)
    validar_frecuencia(m)


def validar_periodica_efectiva(i_p, m):
    validar_tasa_mayor_menos_100(i_p)
    validar_frecuencia(m)


# ---------------------------------------------------------
# MODALIDAD ANTICIPADA Y VENCIDA
# ---------------------------------------------------------

def validar_anticipada_vencida(i_a):
    if i_a < 0 or i_a >= 100:
        raise ValidacionError(
            "La tasa periódica anticipada debe ser mayor o igual "
            "a 0 % y menor que 100 %."
        )


def validar_vencida_anticipada(i_v):
    validar_tasa_no_negativa(i_v)


# ---------------------------------------------------------
# TASAS INDEXADAS
# ---------------------------------------------------------

def validar_dtf_ibr(i1, i2):
    validar_tasa_no_negativa(i1)
    validar_tasa_no_negativa(i2)


def validar_ipc_uvr(i1, i2):
    validar_tasa_mayor_menos_100(i1)
    validar_tasa_mayor_menos_100(i2)


def validar_tasa_indexada(tipo_indexado, i1, i2):
    if tipo_indexado == "IBR + DTF":
        validar_dtf_ibr(i1, i2)

    elif tipo_indexado == "IPC + UVR":
        validar_ipc_uvr(i1, i2)

    else:
        raise ValidacionError(
            "Debes seleccionar un tipo de tasa indexada válido."
        )


# ---------------------------------------------------------
# VALIDAR EL PROCESAMIENTO DE TASAS
# ---------------------------------------------------------

def validar_procesar_tasa(
        tasa,
        tipo_tasa,
        periodicidad_tasa,
        modalidad,
        periodicidad_resultado,
        es_indexada=False,
        tipo_indexado="",
        tasa2=0.0
):
    validar_periodicidad(periodicidad_tasa)
    validar_periodicidad(periodicidad_resultado)

    if es_indexada:
        validar_tasa_indexada(tipo_indexado, tasa, tasa2)

        # Los componentes indexados se interpretan como tasas
        # periódicas de la periodicidad seleccionada.
        validar_tasa_no_negativa(tasa)
        validar_tasa_no_negativa(tasa2)
        return

    validar_tasa_no_negativa(tasa)

    if tipo_tasa not in ["Efectiva anual", "Nominal"]:
        raise ValidacionError(
            "El tipo de tasa debe ser 'Efectiva anual' o 'Nominal'."
        )

    if tipo_tasa == "Nominal":
        if modalidad not in ["Vencida", "Anticipada"]:
            raise ValidacionError(
                "La modalidad debe ser Vencida o Anticipada."
            )

        m = PERIODOS_ANUALES[periodicidad_tasa]

        # En una nominal anticipada, la tasa de descuento de cada
        # período debe ser inferior al 100 %.
        if modalidad == "Anticipada" and (tasa / m) >= 100:
            raise ValidacionError(
                "La tasa anticipada por período debe ser menor que 100 %."
            )


# ---------------------------------------------------------
# VALIDAR CONVERSION DE TIEMPO
# ---------------------------------------------------------

def validar_convertir_tiempo(
        n,
        periodicidad_tiempo,
        periodicidad_resultado
):
    if n < 0:
        raise ValidacionError(
            "El número de períodos no puede ser negativo."
        )

    validar_periodicidad(periodicidad_tiempo)
    validar_periodicidad(periodicidad_resultado)
