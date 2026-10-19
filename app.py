# ---------------------------------------------------------
# app.py
# ---------------------------------------------------------

import streamlit as st

from Utilidades.ValidacionError import ValidacionError

from Modulos.Interes_compuesto import (
    valor_futuro,
    valor_presente,
    valor_interes,
    valor_periodo,
)

from Modulos.Conversiones import (
    PERIODOS_ANUALES,
    procesar_tasa,
    convertir_tiempo,
    anticipada_vencida,
    vencida_anticipada,
)

from Validaciones.Validacion_interes_compuesto import (
    validar_valor_futuro,
    validar_valor_presente,
    validar_valor_interes,
    validar_valor_periodo,
)

from Validaciones.Validacion_conversiones import (
    validar_procesar_tasa,
    validar_convertir_tiempo,
    validar_anticipada_vencida,
    validar_vencida_anticipada,
)


# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------

st.set_page_config(
    page_title="Calculadora financiera", page_icon="💰", layout="centered"
)

st.title("Calculadora financiera")

# Creamos la lista de opciones cambiando "Anual" por "Efectiva anual" solo para la vista
OPCIONES_PERIODICIDAD = [
    "Efectiva anual" if clave == "Anual" else clave
    for clave in PERIODOS_ANUALES.keys()
]


def limpiar_periodicidad(periodicidad_str):
    """Mapea 'Efectiva anual' de vuelta a 'Anual' para el backend."""
    if periodicidad_str == "Efectiva anual":
        return "Anual"
    return periodicidad_str


# ---------------------------------------------------------
# FUNCIONES AUXILIARES PARA LA INTERFAZ
# ---------------------------------------------------------


def ingresar_tasa(key):
    """Permite ingresar una tasa efectiva anual o nominal.

    Si es nominal, solicita su periodicidad de capitalización y su modalidad.
    """

    es_indexada = (
            st.radio(
                "¿La tasa es indexada?",
                ["No", "Sí"],
                key=f"{key}_indexada",
                horizontal=True,
            )
            == "Sí"
    )

    if es_indexada:
        tipo_indexado = st.selectbox(
            "Tipo de tasa indexada", ["IBR + DTF", "IPC + UVR"], key=f"{key}_tipo_indexado"
        )

        tasa1 = st.number_input(
            "Primer componente (%)", min_value=0.0, value=0.0, step=0.1, key=f"{key}_tasa1"
        )

        tasa2 = st.number_input(
            "Segundo componente (%)", min_value=0.0, value=0.0, step=0.1, key=f"{key}_tasa2"
        )

        periodicidad_raw = st.selectbox(
            "Periodicidad de los componentes",
            OPCIONES_PERIODICIDAD,
            index=1,
            key=f"{key}_periodicidad_indexada",
        )
        periodicidad = limpiar_periodicidad(periodicidad_raw)

        return {
            "es_indexada": True,
            "tipo_indexado": tipo_indexado,
            "tasa": tasa1,
            "tasa2": tasa2,
            "tipo_tasa": "Indexada",
            "periodicidad_tasa": periodicidad,
            "modalidad": "Vencida",
        }

    tipo_tasa = st.selectbox(
        "Tipo de tasa", ["Efectiva anual", "Nominal"], key=f"{key}_tipo_tasa"
    )

    tasa = st.number_input(
        "Tasa de interés (%)", min_value=0.0, value=0.0, step=0.1, key=f"{key}_tasa"
    )

    if tipo_tasa == "Efectiva anual":
        periodicidad_tasa = "Anual"
        modalidad = "Vencida"

        st.caption("La tasa efectiva se interpreta como efectiva anual.")

    else:
        periodicidad_raw = st.selectbox(
            "Periodicidad de capitalización de la tasa nominal",
            OPCIONES_PERIODICIDAD,
            index=1,
            key=f"{key}_periodicidad_tasa",
        )
        periodicidad_tasa = limpiar_periodicidad(periodicidad_raw)

        modalidad = st.selectbox(
            "Modalidad de la tasa nominal",
            ["Vencida", "Anticipada"],
            key=f"{key}_modalidad",
        )

    return {
        "es_indexada": False,
        "tipo_indexado": "",
        "tasa": tasa,
        "tasa2": 0.0,
        "tipo_tasa": tipo_tasa,
        "periodicidad_tasa": periodicidad_tasa,
        "modalidad": modalidad,
    }


def calcular_tasa_resultado(datos_tasa, periodicidad_resultado):
    """Valida la tasa ingresada y la convierte a periódica vencida."""

    validar_procesar_tasa(
        tasa=datos_tasa["tasa"],
        tipo_tasa=datos_tasa["tipo_tasa"],
        periodicidad_tasa=datos_tasa["periodicidad_tasa"],
        modalidad=datos_tasa["modalidad"],
        periodicidad_resultado=periodicidad_resultado,
        es_indexada=datos_tasa["es_indexada"],
        tipo_indexado=datos_tasa["tipo_indexado"],
        tasa2=datos_tasa["tasa2"],
    )

    return procesar_tasa(
        tasa=datos_tasa["tasa"],
        tipo_tasa=datos_tasa["tipo_tasa"],
        periodicidad_tasa=datos_tasa["periodicidad_tasa"],
        modalidad=datos_tasa["modalidad"],
        periodicidad_resultado=periodicidad_resultado,
        es_indexada=datos_tasa["es_indexada"],
        tipo_indexado=datos_tasa["tipo_indexado"],
        tasa2=datos_tasa["tasa2"],
    )


def ingresar_tiempo(key):
    """Solicita la cantidad de períodos y su periodicidad."""

    n = st.number_input(
        "Número de períodos", min_value=0.0, value=1.0, step=1.0, key=f"{key}_n"
    )

    periodicidad_raw = st.selectbox(
        "Periodicidad del tiempo",
        OPCIONES_PERIODICIDAD,
        index=1,
        key=f"{key}_periodicidad",
    )
    periodicidad = limpiar_periodicidad(periodicidad_raw)

    return n, periodicidad


def calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_resultado):
    """Valida y convierte el tiempo a la periodicidad de cálculo."""

    validar_convertir_tiempo(n, periodicidad_tiempo, periodicidad_resultado)

    return convertir_tiempo(n, periodicidad_tiempo, periodicidad_resultado)


def mostrar_error(error):
    """Muestra los errores de validación o de cálculo."""

    st.error(getattr(error, "mensaje", str(error)))


# ---------------------------------------------------------
# PESTAÑAS
# ---------------------------------------------------------

tab_interes, tab_conversiones = st.tabs(["Interés compuesto", "Conversiones"])


# =========================================================
# PESTAÑA 1: INTERÉS COMPUESTO
# =========================================================

with tab_interes:

    st.header("Cálculos de interés compuesto")

    operacion = st.selectbox(
        "Selecciona una operación",
        ["Valor futuro", "Valor presente", "Tasa de interés", "Número de períodos"],
        key="operacion_interes",
    )

    st.divider()

    try:

        # -------------------------------------------------
        # VALOR FUTURO
        # -------------------------------------------------

        if operacion == "Valor futuro":

            datos_tasa = ingresar_tasa("futuro")

            P = st.number_input(
                "Valor presente (P)",
                min_value=0.01,
                value=100000.0,
                step=1000.0,
                key="futuro_P",
            )

            n, periodicidad_tiempo = ingresar_tiempo("futuro")

            periodicidad_resultado_raw = st.selectbox(
                "Periodicidad para el cálculo",
                OPCIONES_PERIODICIDAD,
                index=1,
                key="futuro_periodicidad_resultado",
            )
            periodicidad_resultado = limpiar_periodicidad(periodicidad_resultado_raw)

            if st.button("Calcular valor futuro", key="btn_futuro"):

                tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)

                n_resultado = calcular_tiempo_resultado(
                    n, periodicidad_tiempo, periodicidad_resultado
                )

                validar_valor_futuro(P, tasa_calculada, n_resultado)

                resultado = valor_futuro(P, tasa_calculada, n_resultado)

                st.success(f"Valor futuro: ${resultado:,.2f}")
                st.write(f"Tasa periódica vencida utilizada: {tasa_calculada:.6f} %")
                st.write(f"Número de períodos utilizados: {n_resultado:.6f}")

        # -------------------------------------------------
        # VALOR PRESENTE
        # -------------------------------------------------

        elif operacion == "Valor presente":

            datos_tasa = ingresar_tasa("presente")

            F = st.number_input(
                "Valor futuro (F)",
                min_value=0.01,
                value=100000.0,
                step=1000.0,
                key="presente_F",
            )

            n, periodicidad_tiempo = ingresar_tiempo("presente")

            periodicidad_resultado_raw = st.selectbox(
                "Periodicidad para el cálculo",
                OPCIONES_PERIODICIDAD,
                index=1,
                key="presente_periodicidad_resultado",
            )
            periodicidad_resultado = limpiar_periodicidad(periodicidad_resultado_raw)

            if st.button("Calcular valor presente", key="btn_presente"):

                tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)

                n_resultado = calcular_tiempo_resultado(
                    n, periodicidad_tiempo, periodicidad_resultado
                )

                validar_valor_presente(F, tasa_calculada, n_resultado)

                resultado = valor_presente(F, tasa_calculada, n_resultado)

                st.success(f"Valor presente: ${resultado:,.2f}")
                st.write(f"Tasa periódica vencida utilizada: {tasa_calculada:.6f} %")
                st.write(f"Número de períodos utilizados: {n_resultado:.6f}")

        # -------------------------------------------------
        # TASA DE INTERÉS
        # -------------------------------------------------

        elif operacion == "Tasa de interés":

            P = st.number_input(
                "Valor presente (P)",
                min_value=0.01,
                value=100000.0,
                step=1000.0,
                key="interes_P",
            )

            F = st.number_input(
                "Valor futuro (F)",
                min_value=0.01,
                value=120000.0,
                step=1000.0,
                key="interes_F",
            )

            n, periodicidad_tiempo = ingresar_tiempo("interes")

            periodicidad_resultado_raw = st.selectbox(
                "Periodicidad de la tasa que deseas obtener",
                OPCIONES_PERIODICIDAD,
                index=1,
                key="interes_periodicidad_resultado",
            )
            periodicidad_resultado = limpiar_periodicidad(periodicidad_resultado_raw)

            if st.button("Calcular tasa", key="btn_interes"):

                n_resultado = calcular_tiempo_resultado(
                    n, periodicidad_tiempo, periodicidad_resultado
                )

                validar_valor_interes(F, P, n_resultado)

                tasa_calculada = valor_interes(F, P, n_resultado)

                st.success(f"Tasa periódica vencida: {tasa_calculada:.6f} %")
                st.caption(
                    "La tasa calculada corresponde a la periodicidad seleccionada; no"
                    " es una tasa efectiva anual."
                )

        # -------------------------------------------------
        # NÚMERO DE PERÍODOS
        # -------------------------------------------------

        elif operacion == "Número de períodos":

            datos_tasa = ingresar_tasa("periodos")

            P = st.number_input(
                "Valor presente (P)",
                min_value=0.01,
                value=100000.0,
                step=1000.0,
                key="periodos_P",
            )

            F = st.number_input(
                "Valor futuro (F)",
                min_value=0.01,
                value=120000.0,
                step=1000.0,
                key="periodos_F",
            )

            periodicidad_resultado_raw = st.selectbox(
                "Periodicidad en la que deseas obtener los períodos",
                OPCIONES_PERIODICIDAD,
                index=1,
                key="periodos_periodicidad_resultado",
            )
            periodicidad_resultado = limpiar_periodicidad(periodicidad_resultado_raw)

            if st.button("Calcular períodos", key="btn_periodos"):

                tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)

                validar_valor_periodo(F, P, tasa_calculada)

                resultado = valor_periodo(F, P, tasa_calculada)

                st.success(f"Número de períodos: {resultado:.6f}")
                st.caption(
                    f"El resultado está expresado en períodos"
                    f" {periodicidad_resultado.lower()}."
                )

    except (
            ValidacionError,
            ValueError,
            ZeroDivisionError,
            OverflowError,
    ) as error:
        mostrar_error(error)


# =========================================================
# PESTAÑA 2: CONVERSIONES
# =========================================================

with tab_conversiones:

    st.header("Conversiones financieras")

    tipo_conversion = st.selectbox(
        "Selecciona el tipo de conversión",
        ["Convertir tasa", "Convertir tiempo", "Convertir modalidad periódica"],
        key="tipo_conversion",
    )

    st.divider()

    try:

        # -------------------------------------------------
        # CONVERTIR TASA
        # -------------------------------------------------

        if tipo_conversion == "Convertir tasa":

            datos_tasa_conversion = ingresar_tasa("conversion")

            periodicidad_resultado_raw = st.selectbox(
                "Periodicidad de la tasa de resultado",
                OPCIONES_PERIODICIDAD,
                index=1,
                key="conversion_periodicidad_resultado",
            )
            periodicidad_resultado = limpiar_periodicidad(periodicidad_resultado_raw)

            if st.button("Convertir tasa", key="btn_conversion_tasa"):

                resultado = calcular_tasa_resultado(datos_tasa_conversion, periodicidad_resultado)

                st.success(f"Tasa periódica vencida: {resultado:.6f} %")

        # -------------------------------------------------
        # CONVERTIR TIEMPO
        # -------------------------------------------------

        elif tipo_conversion == "Convertir tiempo":

            n, periodicidad_tiempo = ingresar_tiempo("conversion_tiempo")

            periodicidad_resultado_raw = st.selectbox(
                "Periodicidad de resultado",
                OPCIONES_PERIODICIDAD,
                index=2,
                key="conversion_tiempo_resultado",
            )
            periodicidad_resultado = limpiar_periodicidad(periodicidad_resultado_raw)

            if st.button("Convertir tiempo", key="btn_conversion_tiempo"):

                resultado = calcular_tiempo_resultado(
                    n, periodicidad_tiempo, periodicidad_resultado
                )

                st.success(
                    f"Resultado: {resultado:.6f} períodos"
                    f" {periodicidad_resultado.lower()}."
                )

        # -------------------------------------------------
        # CONVERTIR MODALIDAD PERIÓDICA
        # -------------------------------------------------

        elif tipo_conversion == "Convertir modalidad periódica":

            st.info(
                "Esta operación recibe una tasa periódica, no una tasa efectiva"
                " anual. Si partes de una efectiva anual, conviértela primero a"
                " periódica en la opción 'Convertir tasa'."
            )

            tasa_periodica = st.number_input(
                "Tasa periódica (%)",
                min_value=0.0,
                value=2.0,
                step=0.1,
                key="modalidad_tasa",
            )

            modalidad_origen = st.selectbox(
                "Modalidad de origen", ["Anticipada", "Vencida"], key="modalidad_origen"
            )

            if st.button("Convertir modalidad", key="btn_conversion_modalidad"):

                if modalidad_origen == "Anticipada":

                    validar_anticipada_vencida(tasa_periodica)

                    resultado = anticipada_vencida(tasa_periodica)

                    st.success(f"Tasa periódica vencida: {resultado:.6f} %")

                else:

                    validar_vencida_anticipada(tasa_periodica)

                    resultado = vencida_anticipada(tasa_periodica)

                    st.success(f"Tasa periódica anticipada: {resultado:.6f} %")

    except (
            ValidacionError,
            ValueError,
            ZeroDivisionError,
            OverflowError,
    ) as error:
        mostrar_error(error)