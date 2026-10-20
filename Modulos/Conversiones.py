
# ---------------------------------------------------------
# MODULOS/Conversiones.py
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
    "Diaria": 360,
}


def obtener_periodos_anuales(periodicidad: str) -> int:
    """Obtiene cuántos períodos de una periodicidad hay en un año."""
    return PERIODOS_ANUALES[periodicidad]


# ---------------------------------------------------------
# 1. TASA PERIÓDICA Y TASA NOMINAL
# ---------------------------------------------------------

def periodica_nominal(i_p: float, m: int) -> float:
    """Convierte una tasa periódica vencida en nominal anual."""
    return i_p * m


def nominal_periodica(i_n: float, m: int) -> float:
    """Convierte una tasa nominal anual vencida en periódica vencida."""
    return i_n / m


# ---------------------------------------------------------
# 2. TASA NOMINAL Y TASA EFECTIVA ANUAL
# ---------------------------------------------------------

def nominal_efectiva(i_n: float, m: int) -> float:
    """Convierte una tasa nominal anual vencida en efectiva anual."""
    i_p = (i_n / 100) / m
    return ((1 + i_p) ** m - 1) * 100


def efectiva_nominal(i_ea: float, m: int) -> float:
    """Convierte una tasa efectiva anual en nominal anual vencida."""
    i_ea_decimal = i_ea / 100
    i_p = (1 + i_ea_decimal) ** (1 / m) - 1
    return i_p * m * 100


# ---------------------------------------------------------
# 3. TASA EFECTIVA ANUAL Y TASA PERIODICA
# ---------------------------------------------------------

def efectiva_periodica(i_ea: float, m: int) -> float:
    """
    Convierte una tasa efectiva anual en una tasa periódica vencida.
    """
    i_ea_decimal = i_ea / 100
    return ((1 + i_ea_decimal) ** (1 / m) - 1) * 100


def periodica_efectiva(i_p: float, m: int) -> float:
    """
    Convierte una tasa periódica vencida en una tasa efectiva anual.
    """
    i_p_decimal = i_p / 100
    return ((1 + i_p_decimal) ** m - 1) * 100


# ---------------------------------------------------------
# 4. MODALIDAD ANTICIPADA Y VENCIDA
# ---------------------------------------------------------

def anticipada_vencida(i_a: float) -> float:
    """
    Convierte una tasa periódica anticipada en periódica vencida.

    La tasa recibida debe estar expresada para un período,
    por ejemplo, mensual anticipada.
    """
    i_a_decimal = i_a / 100
    return (i_a_decimal / (1 - i_a_decimal)) * 100


def vencida_anticipada(i_v: float) -> float:
    """
    Convierte una tasa periódica vencida en periódica anticipada.

    La tasa recibida debe estar expresada para un período,
    por ejemplo, mensual vencida.
    """
    i_v_decimal = i_v / 100
    return (i_v_decimal / (1 + i_v_decimal)) * 100


# ---------------------------------------------------------
# 5. CONVERSION DE TASAS INDEXADAS
# ---------------------------------------------------------

def dtf_ibr(i1: float, i2: float) -> float:
    """
    Combina dos componentes mediante suma.

    Supone que ambos componentes están expresados en la misma
    unidad y que la convención del ejercicio permite sumarlos.
    """
    return i1 + i2


def ipc_uvr(i1: float, i2: float) -> float:
    """
    Combina dos variaciones mediante composición multiplicativa.
    """
    return (((1 + i1 / 100) * (1 + i2 / 100)) - 1) * 100


def combinar_tasa_indexada(
        tipo_indexado: str,
        i1: float,
        i2: float
) -> float:
    """Combina los componentes de una tasa indexada."""
    if tipo_indexado == "IBR + DTF":
        return dtf_ibr(i1, i2)

    if tipo_indexado == "IPC + UVR":
        return ipc_uvr(i1, i2)

    raise ValueError("Tipo de tasa indexada no reconocido.")


# ---------------------------------------------------------
# 6. CONVERTIR UNA TASA A EFECTIVA ANUAL
# ---------------------------------------------------------

def tasa_a_efectiva_anual(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        modalidad: str = "Vencida"
) -> float:
    """
    Convierte una tasa a efectiva anual.

    - Efectiva anual: se devuelve sin modificar.
    - Nominal vencida: se divide entre la frecuencia y se capitaliza.
    - Nominal anticipada: se obtiene primero la tasa periódica
      anticipada, se convierte a periódica vencida y se capitaliza.
    """
    if tipo_tasa == "Efectiva anual":
        return tasa

    m = obtener_periodos_anuales(periodicidad_tasa)

    # La tasa nominal anual se convierte primero en tasa periódica.
    tasa_periodica = tasa / m

    if modalidad == "Anticipada":
        # Primero se convierte la tasa periódica anticipada
        # en tasa periódica vencida.
        tasa_periodica = anticipada_vencida(tasa_periodica)

    # La tasa utilizada para capitalizar ya es periódica vencida.
    return periodica_efectiva(tasa_periodica, m)


# ---------------------------------------------------------
# 7. CONVERTIR UNA TASA A OTRA PERIODICIDAD
# ---------------------------------------------------------

def convertir_tasa(
        tasa: float,
        tipo_tasa: str,
        periodicidad_tasa: str,
        periodicidad_resultado: str,
        modalidad: str = "Vencida"
) -> float:
    """
    Convierte una tasa a una tasa periódica vencida de destino.

    Primero obtiene la efectiva anual y después la convierte
    a la periodicidad solicitada.
    """
    tasa_ea = tasa_a_efectiva_anual(
        tasa,
        tipo_tasa,
        periodicidad_tasa,
        modalidad
    )

    m_resultado = obtener_periodos_anuales(periodicidad_resultado)

    return efectiva_periodica(tasa_ea, m_resultado)


# ---------------------------------------------------------
# 8. CONVERTIR PERIODOS DE TIEMPO
# ---------------------------------------------------------

def convertir_tiempo(
        n: float,
        periodicidad_tiempo: str,
        periodicidad_resultado: str
) -> float:
    """Convierte una cantidad de períodos a otra periodicidad."""
    m_tiempo = obtener_periodos_anuales(periodicidad_tiempo)
    m_resultado = obtener_periodos_anuales(periodicidad_resultado)

    return n * m_resultado / m_tiempo


# ---------------------------------------------------------
# 9. PROCESAR TASAS NORMALES O INDEXADAS
# ---------------------------------------------------------

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
    """
    Obtiene una tasa periódica vencida para usar en los cálculos.

    Para tasas indexadas, se supone que los componentes se combinan
    según la convención del ejercicio y corresponden a la periodicidad
    seleccionada.
    """
    if es_indexada:
        tasa_combinada = combinar_tasa_indexada(
            tipo_indexado,
            tasa,
            tasa2
        )

        m_tasa = obtener_periodos_anuales(periodicidad_tasa)
        tasa_ea = periodica_efectiva(tasa_combinada, m_tasa)

        m_resultado = obtener_periodos_anuales(periodicidad_resultado)

        return efectiva_periodica(tasa_ea, m_resultado)

    return convertir_tasa(
        tasa,
        tipo_tasa,
        periodicidad_tasa,
        periodicidad_resultado,
        modalidad
    )
