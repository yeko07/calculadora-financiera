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
    convertir_tasa,
    convertir_a_nominal,
)

from Modulos.Anualidades import (
    valor_presente_anualidad_vencida,
    valor_anualidad_con_presente_vencida,
    valor_tiempo_anualidad_vencida_con_presente,
    valor_futuro_anualidad_vencida,
    valor_anualidad_con_futuro_vencida,
    valor_tiempo_anualidad_vencida_con_futuro,
    valor_presente_anualidad_anticipada,
    valor_anualidad_con_presente_anticipada,
    valor_tiempo_anualidad_anticipada_con_presente,
    valor_futuro_anualidad_anticipada,
    valor_anualidad_con_futuro_anticipada,
    valor_tiempo_anualidad_anticipada_con_futuro,
    anualidad_perpetua,
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
)

from Validaciones.Validacion_anualidades import (
    validar_tasa_y_periodos,
    validar_calculo_tiempo_presente_vencida,
    validar_calculo_tiempo_presente_anticipada,
    validar_calculo_tiempo_futuro,
)


# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------

st.set_page_config(
    page_title="Calculadora financiera", page_icon="💰", layout="centered"
)

st.title("Calculadora financiera")

OPCIONES_PERIODICIDAD = list(PERIODOS_ANUALES.keys())


# ---------------------------------------------------------
# FUNCIONES AUXILIARES PARA LA INTERFAZ
# ---------------------------------------------------------


def ingresar_tasa(key):
    """Permite ingresar una tasa efectiva anual, nominal, periódica o indexada."""

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
            "Tipo de tasa indexada", ["IBR o DTF", "IPC o UVR"], key=f"{key}_tipo_indexado"
        )

        tasa1 = st.number_input(
            "Primer componente (%)", min_value=0.0, value=0.0, step=0.1, key=f"{key}_tasa1"
        )

        tasa2 = st.number_input(
            "Segundo componente (%)", min_value=0.0, value=0.0, step=0.1, key=f"{key}_tasa2"
        )

        periodicidad = st.selectbox(
            "Periodicidad de los componentes",
            OPCIONES_PERIODICIDAD,
            index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
            key=f"{key}_periodicidad_indexada",
        )

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
        "Tipo de tasa", ["Efectiva anual", "Nominal", "Periódica"], key=f"{key}_tipo_tasa"
    )

    tasa = st.number_input(
        "Tasa de interés (%)", min_value=0.0, value=0.0, step=0.1, key=f"{key}_tasa"
    )

    if tipo_tasa == "Efectiva anual":
        periodicidad_tasa = "Anual"
        modalidad = "Vencida"
        st.caption("La tasa efectiva se interpreta como efectiva anual.")

    elif tipo_tasa == "Nominal":
        periodicidad_tasa = st.selectbox(
            "Periodicidad de capitalización de la tasa nominal",
            OPCIONES_PERIODICIDAD,
            index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
            key=f"{key}_periodicidad_tasa",
        )

        modalidad = st.selectbox(
            "Modalidad de la tasa nominal",
            ["Vencida", "Anticipada"],
            key=f"{key}_modalidad",
        )

    else:  # Tasa Periódica
        periodicidad_tasa = st.selectbox(
            "Periodicidad de la tasa periódica",
            OPCIONES_PERIODICIDAD,
            index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
            key=f"{key}_periodicidad_tasa",
        )

        modalidad = st.selectbox(
            "Modalidad de la tasa periódica",
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

    periodicidad = st.selectbox(
        "Periodicidad del tiempo",
        OPCIONES_PERIODICIDAD,
        index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
        key=f"{key}_periodicidad",
    )

    return n, periodicidad


def calcular_tiempo_resultado(n, p_tiempo, periodicidad_resultado):
    """Valida y convierte el tiempo a la periodicidad de cálculo."""

    validar_convertir_tiempo(n, p_tiempo, periodicidad_resultado)

    return convertir_tiempo(n, p_tiempo, periodicidad_resultado)


def mostrar_error(error):
    """Muestra los errores de validación o de cálculo."""

    st.error(getattr(error, "mensaje", str(error)))


# ---------------------------------------------------------
# PESTAÑAS
# ---------------------------------------------------------

tab_interes, tab_conversiones, tab_anualidades = st.tabs(
    ["Interés compuesto", "Conversiones", "Anualidades"]
)


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

            periodicidad_resultado = st.selectbox(
                "Periodicidad para el cálculo",
                OPCIONES_PERIODICIDAD,
                index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                key="futuro_periodicidad_resultado",
            )

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

            periodicidad_resultado = st.selectbox(
                "Periodicidad para el cálculo",
                OPCIONES_PERIODICIDAD,
                index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                key="presente_periodicidad_resultado",
            )

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

            periodicidad_resultado = st.selectbox(
                "Periodicidad de la tasa que deseas obtener",
                OPCIONES_PERIODICIDAD,
                index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                key="interes_periodicidad_resultado",
            )

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

            periodicidad_resultado = st.selectbox(
                "Periodicidad en la que deseas obtener los períodos",
                OPCIONES_PERIODICIDAD,
                index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                key="periodos_periodicidad_resultado",
            )

            if st.button("Calcular períodos", key="btn_periodos"):

                tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)

                validar_valor_periodo(F, P, tasa_calculada)

                resultado = valor_periodo(F, P, tasa_calculada)

                st.success(f"Número de períodos: {resultado:.6f}")
                st.caption(
                    f"El resultado está expresado en períodos {periodicidad_resultado.lower()}."
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
        ["Convertir tasa", "Convertir tiempo"],
        key="tipo_conversion",
    )

    st.divider()

    try:

        if tipo_conversion == "Convertir tasa":

            datos_tasa_conversion = ingresar_tasa("conversion")

            tipo_tasa_resultado = st.selectbox(
                "Tipo de tasa de resultado",
                ["Periódica", "Efectiva anual", "Nominal"],
                key="conversion_tipo_tasa_resultado",
            )

            modalidad_resultado = "Vencida"

            if tipo_tasa_resultado == "Efectiva anual":
                periodicidad_resultado = "Anual"
                modalidad_resultado = "Vencida"
                st.caption("La tasa calculada se expresará como Efectiva Anual.")

            elif tipo_tasa_resultado == "Nominal":
                periodicidad_resultado = st.selectbox(
                    "Periodicidad de capitalización del resultado",
                    OPCIONES_PERIODICIDAD,
                    index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                    key="conversion_periodicidad_res_nominal",
                )
                modalidad_resultado = st.selectbox(
                    "Modalidad del resultado",
                    ["Vencida", "Anticipada"],
                    key="conversion_modalidad_res_nominal",
                )

            else:  # Periódica
                periodicidad_resultado = st.selectbox(
                    "Periodicidad de la tasa de resultado",
                    OPCIONES_PERIODICIDAD,
                    index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                    key="conversion_periodicidad_resultado",
                )
                modalidad_resultado = st.selectbox(
                    "Modalidad del resultado",
                    ["Vencida", "Anticipada"],
                    key="conversion_modalidad_res_periodica",
                )

            if st.button("Convertir tasa", key="btn_conversion_tasa"):

                # Extraemos parámetros de entrada para reutilizar el backend unificado
                tasa_val = datos_tasa_conversion["tasa"]
                tipo_tasa_val = datos_tasa_conversion["tipo_tasa"]
                periodicidad_tasa_val = datos_tasa_conversion["periodicidad_tasa"]
                modalidad_val = datos_tasa_conversion["modalidad"]
                es_ind = datos_tasa_conversion["es_indexada"]
                tipo_ind = datos_tasa_conversion["tipo_indexado"]
                tasa2_val = datos_tasa_conversion["tasa2"]

                # Si es indexada, procesamos primero el valor base combinado
                if es_ind:
                    # Usamos la lógica de procesar_tasa o combinada del backend si aplica
                    res_periodica_vencida = calcular_tasa_resultado(
                        datos_tasa_conversion, periodicidad_resultado
                    )
                    if tipo_tasa_resultado == "Efectiva anual":
                        resultado_final = res_periodica_vencida # (Ya calculada como EA en procesar si fuera el caso, pero con convertir_tasa manejamos el flujo)
                    elif tipo_tasa_resultado == "Nominal":
                        resultado_final = convertir_a_nominal(
                            tasa=res_periodica_vencida,
                            tipo_tasa="Periódica",
                            periodicidad_tasa=periodicidad_resultado,
                            periodicidad_resultado=periodicidad_resultado,
                            modalidad="Vencida",
                            modalidad_resultado=modalidad_resultado
                        )
                    else:
                        resultado_final = res_periodica_vencida
                        if modalidad_resultado == "Anticipada":
                            from Modulos.Conversiones import vencida_anticipada
                            resultado_final = vencida_anticipada(resultado_final)
                else:
                    # Flujo estándar optimizado con el backend
                    if tipo_tasa_resultado == "Efectiva anual":
                        from Modulos.Conversiones import tasa_a_efectiva_anual
                        resultado_final = tasa_a_efectiva_anual(
                            tasa=tasa_val,
                            tipo_tasa=tipo_tasa_val,
                            periodicidad_tasa=periodicidad_tasa_val,
                            modalidad=modalidad_val
                        )
                    elif tipo_tasa_resultado == "Nominal":
                        resultado_final = convertir_a_nominal(
                            tasa=tasa_val,
                            tipo_tasa=tipo_tasa_val,
                            periodicidad_tasa=periodicidad_tasa_val,
                            periodicidad_resultado=periodicidad_resultado,
                            modalidad=modalidad_val,
                            modalidad_resultado=modalidad_resultado
                        )
                    else:  # Periódica
                        resultado_final = convertir_tasa(
                            tasa=tasa_val,
                            tipo_tasa=tipo_tasa_val,
                            periodicidad_tasa=periodicidad_tasa_val,
                            periodicidad_resultado=periodicidad_resultado,
                            modalidad=modalidad_val
                        )
                        if modalidad_resultado == "Anticipada":
                            from Modulos.Conversiones import vencida_anticipada
                            resultado_final = vencida_anticipada(resultado_final)

                etiqueta = f"Tasa {tipo_tasa_resultado.lower()} {periodicidad_resultado.lower()} {modalidad_resultado.lower()}"
                if tipo_tasa_resultado == "Efectiva anual":
                    etiqueta = "Tasa efectiva anual"

                st.success(f"{etiqueta}: {resultado_final:.6f} %")

        elif tipo_conversion == "Convertir tiempo":

            n, periodicidad_tiempo = ingresar_tiempo("conversion_tiempo")

            periodicidad_resultado = st.selectbox(
                "Periodicidad de resultado",
                OPCIONES_PERIODICIDAD,
                index=OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0,
                key="conversion_tiempo_resultado",
            )

            if st.button("Convertir tiempo", key="btn_conversion_tiempo"):

                resultado = calcular_tiempo_resultado(
                    n, periodicidad_tiempo, periodicidad_resultado
                )

                st.success(
                    f"Resultado: {resultado:.6f} períodos {periodicidad_resultado.lower()}."
                )

    except (
            ValidacionError,
            ValueError,
            ZeroDivisionError,
            OverflowError,
    ) as error:
        mostrar_error(error)


# =========================================================
# PESTAÑA 3: ANUALIDADES
# =========================================================

with tab_anualidades:

    st.header("Cálculos de anualidades")

    sub_anualidad = st.selectbox(
        "Selecciona el tipo de anualidad",
        [
            "Anualidades Vencidas",
            "Anualidades Anticipadas",
            "Anualidades Perpetuas",
        ],
        key="sub_anualidad",
    )

    st.divider()

    try:
        if sub_anualidad == "Anualidades Vencidas":
            operacion_vencida = st.selectbox(
                "Selecciona la operación (Vencidas)",
                [
                    "Valor Presente (P)",
                    "Anualidad (A) desde Presente",
                    "Tiempo (n) desde Presente",
                    "Valor Futuro (F)",
                    "Anualidad (A) desde Futuro",
                    "Tiempo (n) desde Futuro",
                ],
                key="op_vencida",
            )

            if operacion_vencida == "Valor Presente (P)":
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="v_p_A")
                datos_tasa = ingresar_tasa("v_p_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("v_p_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="v_p_per")

                if st.button("Calcular Valor Presente", key="btn_v_p"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_presente_anualidad_vencida(A, tasa_calc, int(n_calc))
                    st.success(f"Valor Presente (P): ${resultado:,.2f}")

            elif operacion_vencida == "Anualidad (A) desde Presente":
                P = st.number_input("Valor Presente (P)", value=10000.0, step=1000.0, key="v_a_p_P")
                datos_tasa = ingresar_tasa("v_a_p_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("v_a_p_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="v_a_p_per")

                if st.button("Calcular Anualidad (A)", key="btn_v_a_p"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_anualidad_con_presente_vencida(P, tasa_calc, int(n_calc))
                    st.success(f"Anualidad (A): ${resultado:,.2f}")

            elif operacion_vencida == "Tiempo (n) desde Presente":
                P = st.number_input("Valor Presente (P)", value=10000.0, step=1000.0, key="t_p_P")
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="t_p_A")
                datos_tasa = ingresar_tasa("t_p_tasa")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="t_p_per")

                if st.button("Calcular Tiempo (n)", key="btn_t_p"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    validar_calculo_tiempo_presente_vencida(P, tasa_calc, A)

                    resultado = valor_tiempo_anualidad_vencida_con_presente(P, tasa_calc, A)
                    st.success(f"Número de períodos (n): {resultado:.4f}")

            elif operacion_vencida == "Valor Futuro (F)":
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="v_f_A")
                datos_tasa = ingresar_tasa("v_f_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("v_f_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="v_f_per")

                if st.button("Calcular Valor Futuro", key="btn_v_f"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_futuro_anualidad_vencida(A, tasa_calc, int(n_calc))
                    st.success(f"Valor Futuro (F): ${resultado:,.2f}")

            elif operacion_vencida == "Anualidad (A) desde Futuro":
                F = st.number_input("Valor Futuro (F)", value=15000.0, step=1000.0, key="v_a_f_F")
                datos_tasa = ingresar_tasa("v_a_f_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("v_a_f_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="v_a_f_per")

                if st.button("Calcular Anualidad (A)", key="btn_v_a_f"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_anualidad_con_futuro_vencida(F, tasa_calc, int(n_calc))
                    st.success(f"Anualidad (A): ${resultado:,.2f}")

            elif operacion_vencida == "Tiempo (n) desde Futuro":
                F = st.number_input("Valor Futuro (F)", value=15000.0, step=1000.0, key="t_f_F")
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="t_f_A")
                datos_tasa = ingresar_tasa("t_f_tasa")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="t_f_per")

                if st.button("Calcular Tiempo (n)", key="btn_t_f"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    validar_calculo_tiempo_futuro(A, tasa_calc)

                    resultado = valor_tiempo_anualidad_vencida_con_futuro(F, tasa_calc, A)
                    st.success(f"Número de períodos (n): {resultado:.4f}")

        elif sub_anualidad == "Anualidades Anticipadas":
            operacion_anticipada = st.selectbox(
                "Selecciona la operación (Anticipadas)",
                [
                    "Valor Presente (P)",
                    "Anualidad (A) desde Presente",
                    "Tiempo (n) desde Presente",
                    "Valor Futuro (F)",
                    "Anualidad (A) desde Futuro",
                    "Tiempo (n) desde Futuro",
                ],
                key="op_anticipada",
            )

            if operacion_anticipada == "Valor Presente (P)":
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="ant_p_A")
                datos_tasa = ingresar_tasa("ant_p_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("ant_p_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="ant_p_per")

                if st.button("Calcular Valor Presente Anticipado", key="btn_ant_p"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_presente_anualidad_anticipada(A, tasa_calc, int(n_calc))
                    st.success(f"Valor Presente Anticipado (P): ${resultado:,.2f}")

            elif operacion_anticipada == "Anualidad (A) desde Presente":
                P = st.number_input("Valor Presente (P)", value=10000.0, step=1000.0, key="ant_ap_P")
                datos_tasa = ingresar_tasa("ant_ap_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("ant_ap_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="ant_ap_per")

                if st.button("Calcular Anualidad Anticipada (A)", key="btn_ant_ap"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_anualidad_con_presente_anticipada(P, tasa_calc, int(n_calc))
                    st.success(f"Anualidad Anticipada (A): ${resultado:,.2f}")

            elif operacion_anticipada == "Tiempo (n) desde Presente":
                P = st.number_input("Valor Presente (P)", value=10000.0, step=1000.0, key="ant_tp_P")
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="ant_tp_A")
                datos_tasa = ingresar_tasa("ant_tp_tasa")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="ant_tp_per")

                if st.button("Calcular Tiempo (n) Anticipado", key="btn_ant_tp"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    validar_calculo_tiempo_presente_anticipada(P, tasa_calc, A)

                    resultado = valor_tiempo_anualidad_anticipada_con_presente(P, tasa_calc, A)
                    st.success(f"Número de períodos (n): {resultado:.4f}")

            elif operacion_anticipada == "Valor Futuro (F)":
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="ant_f_A")
                datos_tasa = ingresar_tasa("ant_f_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("ant_f_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="ant_f_per")

                if st.button("Calcular Valor Futuro Anticipado", key="btn_ant_f"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_futuro_anualidad_anticipada(A, tasa_calc, int(n_calc))
                    st.success(f"Valor Futuro Anticipado (F): ${resultado:,.2f}")

            elif operacion_anticipada == "Anualidad (A) desde Futuro":
                F = st.number_input("Valor Futuro (F)", value=15000.0, step=1000.0, key="ant_af_F")
                datos_tasa = ingresar_tasa("ant_af_tasa")
                n, periodicidad_tiempo = ingresar_tiempo("ant_af_n")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="ant_af_per")

                if st.button("Calcular Anualidad Anticipada (A)", key="btn_ant_af"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    n_calc = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_res)
                    validar_tasa_y_periodos(tasa_calc, int(n_calc))

                    resultado = valor_anualidad_con_futuro_anticipada(F, tasa_calc, int(n_calc))
                    st.success(f"Anualidad Anticipada (A): ${resultado:,.2f}")

            elif operacion_anticipada == "Tiempo (n) desde Futuro":
                F = st.number_input("Valor Futuro (F)", value=15000.0, step=1000.0, key="ant_tf_F")
                A = st.number_input("Valor de la anualidad (A)", value=1000.0, step=100.0, key="ant_tf_A")
                datos_tasa = ingresar_tasa("ant_tf_tasa")
                periodicidad_res = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="ant_tf_per")

                if st.button("Calcular Tiempo (n) Anticipado", key="btn_ant_tf"):
                    tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
                    resultado = valor_tiempo_anualidad_anticipada_con_futuro(F, tasa_calc, A)
                    st.success(f"Número de períodos (n): {resultado:.4f}")

        elif sub_anualidad == "Anualidades Perpetuas":
            st.info("Cálculos para anualidades perpetuas.")
            A_perp = st.number_input("Valor de la anualidad perpetua (A)", value=1000.0, step=100.0, key="perp_A")
            datos_tasa_perp = ingresar_tasa("perp_tasa")
            periodicidad_perp = st.selectbox("Periodicidad de cálculo", OPCIONES_PERIODICIDAD, key="perp_per")

            if st.button("Calcular Valor Presente Perpetuo", key="btn_perp"):
                tasa_calc_perp = calcular_tasa_resultado(datos_tasa_perp, periodicidad_perp)
                resultado_perp = anualidad_perpetua(A_perp, tasa_calc_perp)
                st.success(f"Valor Presente Perpetuo (P): ${resultado_perp:,.2f}")

    except (
            ValidacionError,
            ValueError,
            ZeroDivisionError,
            OverflowError,
    ) as error:
        mostrar_error(error)