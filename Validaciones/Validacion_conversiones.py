# ---------------------------------------------------------
# VALIDACIONES/Validacion_conversiones.py
# Validaciones previas a Modulos/Conversiones.py.
# Políticas:
#  - Tasas normales (EA, nominal, periódica): finitas y >= 0.
#  - Tasas anticipadas: >= 0 y < 100 % por período.
#  - La EA NO admite modalidad anticipada (ni como entrada ni como resultado).
#  - IPC/UVR sí puede ser negativo (> -100 %); IBR/DTF no.
# ---------------------------------------------------------

from Utilidades.ValidacionError import ValidacionError
from Utilidades.Numeros import exigir_numero, es_numero_finito
from Modulos.Conversiones import (
    PERIODOS_ANUALES,
    PAR_SIN_EQUIVALENCIA,
    tasa_total_a_efectiva_anual,
)

TIPOS_TASA = ["Efectiva anual", "Nominal", "Periódica"]
MODALIDADES = ["Vencida", "Anticipada"]
MSG_TASA = "La tasa es obligatoria y debe ser un número finito."


# ---------------------------------------------------------
# VALIDACIONES BÁSICAS
# ---------------------------------------------------------

def validar_periodicidad(periodicidad: str) -> None:
    """La periodicidad debe existir en PERIODOS_ANUALES."""
    if periodicidad is None or periodicidad not in PERIODOS_ANUALES:
        raise ValidacionError(f"La periodicidad '{periodicidad}' no es válida.")


def validar_frecuencia(m: float) -> None:
    """La frecuencia de capitalización debe ser finita y mayor que cero."""
    exigir_numero(m, "La frecuencia de capitalización es obligatoria.")
    if m <= 0:
        raise ValidacionError(
            "La frecuencia de capitalización debe ser mayor que cero."
        )


def validar_tasa_no_negativa(tasa: float) -> None:
    """La tasa debe ser finita y mayor o igual a cero."""
    exigir_numero(tasa, MSG_TASA)
    if tasa < 0:
        raise ValidacionError("La tasa de interés no puede ser negativa.")


def validar_tasa_mayor_menos_100(tasa: float) -> None:
    """La tasa debe ser finita y mayor que -100 % (uso: IPC/UVR)."""
    exigir_numero(tasa, MSG_TASA)
    if tasa <= -100:
        raise ValidacionError("La tasa debe ser mayor que -100 %.")


def validar_modalidad(modalidad: str) -> None:
    """La modalidad debe ser Vencida o Anticipada."""
    if modalidad not in MODALIDADES:
        raise ValidacionError("La modalidad debe ser Vencida o Anticipada.")


def validar_ea_sin_modalidad_anticipada(tipo: str, modalidad: str, contexto: str) -> None:
    """Rechaza la combinación Efectiva anual + Anticipada.

    `contexto` indica si es la entrada o el resultado, para el mensaje.
    """
    if tipo == "Efectiva anual" and modalidad == "Anticipada":
        raise ValidacionError(
            f"La tasa efectiva anual {contexto} no admite modalidad "
            "anticipada: la EA siempre es vencida."
        )


# ---------------------------------------------------------
# TASA PERIÓDICA Y NOMINAL
# ---------------------------------------------------------

def validar_periodica_nominal(i_p: float, m: float) -> None:
    """Valida i_p y m para periódica -> nominal."""
    validar_tasa_no_negativa(i_p)
    validar_frecuencia(m)


def validar_nominal_periodica(i_n: float, m: float) -> None:
    """Valida i_n y m para nominal -> periódica."""
    validar_tasa_no_negativa(i_n)
    validar_frecuencia(m)


# ---------------------------------------------------------
# TASA NOMINAL Y TASA EFECTIVA ANUAL
# ---------------------------------------------------------

def validar_nominal_efectiva(i_n: float, m: float) -> None:
    """Valida i_n y m para nominal -> EA."""
    validar_tasa_no_negativa(i_n)
    validar_frecuencia(m)


def validar_efectiva_nominal(i_ea: float, m: float) -> None:
    """Valida i_ea y m para EA -> nominal."""
    validar_tasa_no_negativa(i_ea)
    validar_frecuencia(m)


# ---------------------------------------------------------
# TASA EFECTIVA ANUAL Y PERIÓDICA
# ---------------------------------------------------------

def validar_efectiva_periodica(i_ea: float, m: float) -> None:
    """Valida i_ea y m para EA -> periódica (mismo criterio que el resto)."""
    validar_tasa_no_negativa(i_ea)
    validar_frecuencia(m)


def validar_periodica_efectiva(i_p: float, m: float) -> None:
    """Valida i_p y m para periódica -> EA (mismo criterio que el resto)."""
    validar_tasa_no_negativa(i_p)
    validar_frecuencia(m)


# ---------------------------------------------------------
# MODALIDAD ANTICIPADA Y VENCIDA
# ---------------------------------------------------------

def validar_anticipada_vencida(i_a: float) -> None:
    """La tasa anticipada por período debe estar en [0 %, 100 %)."""
    exigir_numero(i_a, MSG_TASA)
    if i_a < 0 or i_a >= 100:
        raise ValidacionError(
            "La tasa periódica anticipada debe ser mayor o igual "
            "a 0 % y menor que 100 %."
        )


def validar_vencida_anticipada(i_v: float) -> None:
    """La tasa vencida debe ser finita y no negativa."""
    validar_tasa_no_negativa(i_v)


# ---------------------------------------------------------
# TASAS INDEXADAS
# ---------------------------------------------------------

def validar_dtf_ibr(i1: float, i2: float) -> None:
    """IBR/DTF y su spread no pueden ser negativos."""
    validar_tasa_no_negativa(i1)
    validar_tasa_no_negativa(i2)


def validar_ipc_uvr(i1: float, i2: float) -> None:
    """IPC/UVR y su spread pueden ser negativos, pero mayores que -100 %."""
    validar_tasa_mayor_menos_100(i1)
    validar_tasa_mayor_menos_100(i2)


def validar_tasa_indexada(tipo_indexado: str, i1: float, i2: float) -> None:
    """Valida los dos componentes según el tipo de tasa indexada."""
    if tipo_indexado == "IBR o DTF":
        validar_dtf_ibr(i1, i2)
    elif tipo_indexado == "IPC o UVR":
        validar_ipc_uvr(i1, i2)
    else:
        raise ValidacionError("Debes seleccionar un tipo de tasa indexada válido.")


# ---------------------------------------------------------
# VERIFICACIÓN DE CÁLCULO (ensayo en seco)
# ---------------------------------------------------------

def _verificar_ea_calculable(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        es_indexada, tipo_indexado, tasa2
) -> None:
    """Calcula la EA en seco para detectar desbordamientos o resultados inválidos."""
    try:
        ea = tasa_total_a_efectiva_anual(
            tasa, tipo_tasa, periodicidad_tasa, modalidad,
            es_indexada, tipo_indexado, tasa2
        )
    except (OverflowError, ZeroDivisionError, ValueError):
        ea = None

    if ea is None or not es_numero_finito(ea):
        raise ValidacionError(
            "Con esos datos la tasa efectiva anual no puede calcularse "
            "(el valor es demasiado grande o inválido)."
        )


# ---------------------------------------------------------
# PROCESAMIENTO DE TASAS
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
) -> None:
    """Valida los datos de entrada de una tasa normal o indexada."""
    # Las periodicidades de entrada y salida deben existir.
    validar_periodicidad(periodicidad_tasa)
    validar_periodicidad(periodicidad_resultado)

    if es_indexada:
        # Indexadas: solo importan el tipo y los dos componentes
        # (tipo_tasa y modalidad se ignoran).
        validar_tasa_indexada(tipo_indexado, tasa, tasa2)
    else:
        # Tasas normales: todos los campos son obligatorios.
        if tipo_tasa is None or modalidad is None:
            raise ValidacionError("Todos los campos de la tasa son obligatorios.")

        if tipo_tasa not in TIPOS_TASA:
            raise ValidacionError(
                "El tipo de tasa debe ser 'Efectiva anual', 'Nominal' o 'Periódica'."
            )

        validar_tasa_no_negativa(tasa)
        validar_modalidad(modalidad)

        # La EA es siempre vencida.
        validar_ea_sin_modalidad_anticipada(tipo_tasa, modalidad, "de entrada")

        if modalidad == "Anticipada":
            # Tasa anticipada por período: nominal se divide entre m;
            # en Periódica la tasa ya es por período.
            m = PERIODOS_ANUALES[periodicidad_tasa] if tipo_tasa == "Nominal" else 1
            if (tasa / m) >= 100:
                raise ValidacionError(
                    "La tasa anticipada por período debe ser menor que 100 %."
                )

    # Ensayo en seco: evita desbordamientos en la conversión a EA.
    _verificar_ea_calculable(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        es_indexada, tipo_indexado, tasa2
    )


# ---------------------------------------------------------
# CONVERSIÓN COMPLETA
# ---------------------------------------------------------

def validar_convertir_tasa_completa(
        tasa,
        tipo_tasa,
        periodicidad_tasa,
        modalidad,
        tipo_resultado,
        periodicidad_resultado,
        modalidad_resultado,
        es_indexada=False,
        tipo_indexado="",
        tasa2=0.0
) -> None:
    """Valida los datos de entrada y los del resultado deseado."""
    # Valida la tasa de entrada.
    validar_procesar_tasa(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        periodicidad_resultado, es_indexada, tipo_indexado, tasa2
    )

    # Valida el tipo y la modalidad del resultado.
    if tipo_resultado not in TIPOS_TASA:
        raise ValidacionError("El tipo de tasa de resultado no es válido.")

    validar_modalidad(modalidad_resultado)

    # La EA como resultado tampoco puede ser anticipada.
    validar_ea_sin_modalidad_anticipada(
        tipo_resultado, modalidad_resultado, "de resultado"
    )


# ---------------------------------------------------------
# CONVERSIÓN DE TIEMPO
# ---------------------------------------------------------

def validar_convertir_tiempo(
        n,
        periodicidad_tiempo,
        periodicidad_resultado
) -> None:
    """Valida n y las periodicidades antes de convertir tiempo."""
    exigir_numero(n, "El número de períodos es obligatorio y debe ser un número finito.")

    if n < 0:
        raise ValidacionError("El número de períodos no puede ser negativo.")

    validar_periodicidad(periodicidad_tiempo)
    validar_periodicidad(periodicidad_resultado)

    # Semanas <-> días no tienen equivalencia exacta con el año de 360 días.
    if {periodicidad_tiempo, periodicidad_resultado} == PAR_SIN_EQUIVALENCIA:
        raise ValidacionError(
            "No hay equivalencia exacta entre semanas y días "
            "(52 semanas = 364 días; el año comercial tiene 360). "
            "Elige otra periodicidad."
        )