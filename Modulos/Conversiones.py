# ---------------------------------------------------------
# MODULOS/Conversiones.py
# Modelo unificado de conversión de tasas.
#
# Convención: toda tasa se expresa en porcentaje (5 = 5 %).
# Pivote: cualquier tasa de entrada se lleva primero a Efectiva Anual (EA,
# siempre vencida) y desde ahí se obtiene la tasa periódica vencida de la
# periodicidad pedida. Luego, si corresponde, se pasa a anticipada y/o a
# nominal. La Efectiva Anual NO admite modalidad anticipada.
# Las validaciones de datos están en Validaciones/Validacion_conversiones.py.
# ---------------------------------------------------------

# Número de períodos por año según la periodicidad.
PERIODOS_ANUALES = {
    "Anual": 1,
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Cuatrimestral": 3,
    "Semestral": 2,
    "Quincenal": 24,
    "Semanal": 52,
    "Diaria": 360,   # Año comercial de 360 días
}

# Par de periodicidades sin equivalencia exacta: 52 semanas = 364 días,
# pero el año comercial diario tiene 360 días (1 semana saldría en 6,92 días).
PAR_SIN_EQUIVALENCIA = frozenset({"Semanal", "Diaria"})


def obtener_periodos_anuales(periodicidad: str) -> int:
    """Devuelve cuántos períodos de una periodicidad hay en un año."""
    if periodicidad not in PERIODOS_ANUALES:
        raise ValueError(f"Periodicidad no reconocida: '{periodicidad}'.")
    return PERIODOS_ANUALES[periodicidad]


# ---------------------------------------------------------
# 1. TASA PERIÓDICA Y TASA NOMINAL
# ---------------------------------------------------------

def periodica_nominal(i_p: float, m: int) -> float:
    """Periódica -> nominal anual: (misma modalidad)."""
    i_p_decimal = i_p/100
    return i_p_decimal * m *100


def nominal_periodica(i_n: float, m: int) -> float:
    """Nominal anual -> periódica: (misma modalidad)."""
    i_n_decimal = i_n/100
    return (i_n / m) * 100


# ---------------------------------------------------------
# 2. TASA NOMINAL Y TASA EFECTIVA ANUAL (nominal vencida)
# ---------------------------------------------------------

def nominal_efectiva(i_n: float, m: int) -> float:
    """Nominal vencida -> EA"""
    i_p = (i_n / 100) / m
    return ((1 + i_p) ** m - 1) * 100


def efectiva_nominal(i_ea: float, m: int) -> float:
    """EA -> nominal vencida"""
    i_ea_decimal = i_ea / 100
    i_p = (1 + i_ea_decimal) ** (1 / m) - 1
    return i_p * m * 100


# ---------------------------------------------------------
# 3. TASA EFECTIVA ANUAL Y TASA PERIÓDICA (vencida)
# ---------------------------------------------------------

def efectiva_periodica(i_ea: float, m: int) -> float:
    """EA -> periódica vencida"""
    i_ea_decimal = i_ea / 100
    return ((1 + i_ea_decimal) ** (1 / m) - 1) * 100


def periodica_efectiva(i_p: float, m: int) -> float:
    """Periódica vencida -> EA"""
    i_p_decimal = i_p / 100
    return ((1 + i_p_decimal) ** m - 1) * 100

###############################################################################################################

# ---------------------------------------------------------
# 4. MODALIDAD ANTICIPADA Y VENCIDA (tasas de un mismo período)
# ---------------------------------------------------------

def anticipada_vencida(i_a: float) -> float:
    """Periódica anticipada -> vencida

    Requiere i_a < 100 %. La tasa debe corresponder al mismo período
    (por ejemplo, mensual anticipada -> mensual vencida).
    """
    i_a_decimal = i_a / 100
    return (i_a_decimal / (1 - i_a_decimal)) * 100


def vencida_anticipada(i_v: float) -> float:
    """Periódica vencida -> anticipada"""
    i_v_decimal = i_v / 100
    return (i_v_decimal / (1 + i_v_decimal)) * 100

#######################################################################################################################


# ---------------------------------------------------------
# 5. TASAS INDEXADAS (dos tasas)
# ---------------------------------------------------------

def dtf_ibr(i1: float, i2: float) -> float:
    """IBR/DTF + spread: suma de las dos tasas.

    Ambas tasas son periódicas
    vencidas de la periodicidad elegida (no se usa la modalidad).
    """
    return i1 + i2


def ipc_uvr(i1: float, i2: float) -> float:
    """IPC/UVR + spread"""
    return (((1 + i1 / 100) * (1 + i2 / 100)) - 1) * 100


def combinar_tasa_indexada(tipo_indexado: str, i1: float, i2: float) -> float:
    """Combina los componentes según el tipo de tasa indexada."""
    if tipo_indexado == "IBR o DTF":
        return dtf_ibr(i1, i2)

    if tipo_indexado == "IPC o UVR":
        return ipc_uvr(i1, i2)

    raise ValueError("Tipo de tasa indexada no reconocido.")


# ---------------------------------------------------------
# 6. CUALQUIER TASA -> EFECTIVA ANUAL (siempre vencida)
# ---------------------------------------------------------

def tasa_a_efectiva_anual(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        modalidad: str = "Vencida"
) -> float:
    """Convierte una tasa Efectiva anual, Nominal o Periódica a EA vencida."""

    # La EA no admite modalidad anticipada.
    if tipo_tasa == "Efectiva anual":
        if modalidad == "Anticipada":
            raise ValueError(
                "La tasa efectiva anual no admite modalidad anticipada."
            )
        return tasa

    # Para Nominal y Periódica se necesita m (períodos por año).
    m = obtener_periodos_anuales(periodicidad_tasa)

    if tipo_tasa == "Nominal":
        if modalidad == "Anticipada":
            # se pasa de nominal anticipada a periodica anticipada
            tasa_p_anticipada = nominal_periodica(tasa, m)
            # Periódica anticipada -> periódica vencida.
            tasa_p_vencida = anticipada_vencida(tasa_p_anticipada)
            # Periódica vencida -> EA.
            return periodica_efectiva(tasa_p_vencida, m)
        return nominal_efectiva(tasa, m)

    if tipo_tasa == "Periódica":
        tasa_p = tasa
        # Si es anticipada, primero pasa a vencida.
        if modalidad == "Anticipada":
            tasa_p = anticipada_vencida(tasa_p)
        return periodica_efectiva(tasa_p, m)

    raise ValueError(f"Tipo de tasa no reconocido: '{tipo_tasa}'.")


def tasa_indexada_a_efectiva_anual(
        tipo_indexado: str,
        i1: float,
        i2: float,
        periodicidad_tasa: str
) -> float:
    """
    Las tasas se interpretan como periódicas vencidas de la
    periodicidad indicada.
    """

    tasa_combinada = combinar_tasa_indexada(tipo_indexado, i1, i2)
    m_tasa = obtener_periodos_anuales(periodicidad_tasa)
    if periodicidad_tasa == "Anual":
        return tasa_combinada
    return periodica_efectiva(tasa_combinada, m_tasa)


def tasa_total_a_efectiva_anual(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        modalidad: str = "Vencida",
        es_indexada: bool = False,
        tipo_indexado: str = "",
        tasa2: float = 0.0
) -> float:
    """Lleva una tasa normal o indexada a EA."""
    # Las tasas indexadas ignoran tipo_tasa y modalidad.
    if es_indexada:
        return tasa_indexada_a_efectiva_anual(
            tipo_indexado, tasa, tasa2, periodicidad_tasa
        )

    return tasa_a_efectiva_anual(tasa, tipo_tasa, periodicidad_tasa, modalidad)


# ---------------------------------------------------------
# 7. CONVERSIÓN COMPLETA
# ---------------------------------------------------------

def convertir_tasa_completa(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        modalidad: str,
        tipo_resultado: str,
        periodicidad_resultado: str,
        modalidad_resultado: str = "Vencida",
        es_indexada: bool = False,
        tipo_indexado: str = "",
        tasa2: float = 0.0
) -> float:
    """Convierte cualquier tasa (normal o indexada) a EA, Periódica o Nominal.

    El resultado Periódico o Nominal puede ser vencido o anticipado; el
    resultado Efectivo anual solo puede ser vencido.
    """
    # La EA no admite modalidad anticipada, tampoco como resultado.
    if tipo_resultado == "Efectiva anual" and modalidad_resultado == "Anticipada":
        raise ValueError(
            "La tasa efectiva anual no admite modalidad anticipada."
        )


    tasa_ea = tasa_total_a_efectiva_anual(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        es_indexada, tipo_indexado, tasa2
    )

    if tipo_resultado == "Efectiva anual":
        return tasa_ea

    # EA -> periódica vencida de la periodicidad de salida.
    m_resultado = obtener_periodos_anuales(periodicidad_resultado)
    i_p = efectiva_periodica(tasa_ea, m_resultado)

    #  si se pide anticipada, convertir en el mismo período.
    if modalidad_resultado == "Anticipada":
        i_p = vencida_anticipada(i_p)

    if tipo_resultado == "Periódica":
        return i_p

    # nominal = periódica · m (misma modalidad que la periódica).
    if tipo_resultado == "Nominal":
        return periodica_nominal(i_p, m_resultado)

    raise ValueError(f"Tipo de tasa de resultado no reconocido: '{tipo_resultado}'.")


# ---------------------------------------------------------
# 8. ATAJOS DE CONVERSIÓN (usan convertir_tasa_completa)
# ---------------------------------------------------------

def convertir_tasa(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        periodicidad_resultado: str,
        modalidad: str = "Vencida",
        modalidad_resultado = "Vencida"
) -> float:
    """Cualquier tasa (no indexada) -> periódica vencida o anticipada."""
    return convertir_tasa_completa(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        "Periódica", periodicidad_resultado, "Vencida"
    )


def convertir_a_nominal(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        periodicidad_resultado: str,
        modalidad: str = "Vencida",
        modalidad_resultado: str = "Vencida"
) -> float:
    """Cualquier tasa (no indexada) -> nominal anual vencida o anticipada."""
    return convertir_tasa_completa(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        "Nominal", periodicidad_resultado, modalidad_resultado
    )


def procesar_tasa(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        modalidad: str,
        periodicidad_resultado: str,
        es_indexada: bool = False,
        tipo_indexado: str = "",
        tasa2: float = 0.0
) -> float:
    """Obtiene la tasa periódica VENCIDA que usan los cálculos financieros."""
    return convertir_tasa_completa(
        tasa, tipo_tasa, periodicidad_tasa, modalidad,
        "Periódica", periodicidad_resultado, "Vencida",
        es_indexada, tipo_indexado, tasa2
    )


# ---------------------------------------------------------
# 9. CONVERTIR PERÍODOS DE TIEMPO
# ---------------------------------------------------------

def convertir_tiempo(
        n: float,
        periodicidad_tiempo: str,
        periodicidad_resultado: str
) -> float:
    """Convierte una cantidad de períodos a otra periodicidad.

    No se admite Semanal <-> Diaria (52 semanas ≠ 360 días).
    """
    if {periodicidad_tiempo, periodicidad_resultado} == PAR_SIN_EQUIVALENCIA:
        raise ValueError(
            "No hay equivalencia exacta entre semanas y días "
            "(52 semanas = 364 días, año comercial = 360)."
        )

    m_tiempo = obtener_periodos_anuales(periodicidad_tiempo)
    m_resultado = obtener_periodos_anuales(periodicidad_resultado)

    # n períodos de A equivalen a n·(m_resultado / m_tiempo) períodos de B.
    return n * m_resultado / m_tiempo