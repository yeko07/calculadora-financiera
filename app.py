# ---------------------------------------------------------
# app.py
# ---------------------------------------------------------
# Interfaz: navegación en la barra lateral; en cada pantalla los
# datos van a la izquierda y el resultado a la derecha.

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
    convertir_tasa_completa,
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
    validar_convertir_tasa_completa,
)

from Validaciones.Validacion_anualidades import (
    validar_anualidad_con_periodos,
    validar_calculo_tiempo_presente_vencida,
    validar_calculo_tiempo_presente_anticipada,
    validar_calculo_tiempo_futuro,
    validar_calculo_perpetua,
)


# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------

st.set_page_config(
    page_title="Calculadora financiera", page_icon="💰", layout="wide"
)

OPCIONES_PERIODICIDAD = list(PERIODOS_ANUALES.keys())
INDICE_MENSUAL = OPCIONES_PERIODICIDAD.index("Mensual") if "Mensual" in OPCIONES_PERIODICIDAD else 0

ERRORES_CONTROLADOS = (
    ValidacionError,
    ValueError,
    ZeroDivisionError,
    OverflowError,
)


# ---------------------------------------------------------
# FUNCIONES AUXILIARES PARA LA INTERFAZ
# ---------------------------------------------------------

def selector_periodicidad(etiqueta, key):
    """Selector de periodicidad con 'Mensual' como valor por defecto."""
    return st.selectbox(
        etiqueta, OPCIONES_PERIODICIDAD, index=INDICE_MENSUAL, key=key
    )


def ingresar_monto(etiqueta, valor, key):
    """Valor monetario positivo (A, P o F)."""
    return st.number_input(
        etiqueta, min_value=0.01, max_value=1e12, value=valor, step=100.0, key=key
    )


def ingresar_tasa(key):
    """Permite ingresar una tasa efectiva anual, nominal, periódica o indexada con total libertad."""

    with st.container(border=True):
        st.markdown("**Tasa de interés**")

        es_indexada = st.toggle(
            "Es una tasa indexada (DTF, IBR, IPC o UVR)", key=f"{key}_indexada"
        )

        if es_indexada:
            col_a, col_b = st.columns(2)

            with col_a:
                tipo_indexado = st.selectbox(
                    "Tipo de tasa indexada",
                    ["IBR o DTF", "IPC o UVR"],
                    key=f"{key}_tipo_indexado",
                )

            with col_b:
                periodicidad = selector_periodicidad(
                    "Periodicidad de los componentes", f"{key}_periodicidad_indexada"
                )

            col_c, col_d = st.columns(2)

            with col_c:
                tasa1 = st.number_input(
                    "Primer componente (%)", min_value=-99.99, max_value=1000.0,
                    value=0.0, step=0.1, key=f"{key}_tasa1",
                )

            with col_d:
                tasa2 = st.number_input(
                    "Segundo componente (%)", min_value=-99.99, max_value=1000.0,
                    value=0.0, step=0.1, key=f"{key}_tasa2",
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

        col_a, col_b = st.columns(2)

        with col_a:
            tipo_tasa = st.selectbox(
                "Tipo de tasa",
                ["Efectiva anual", "Nominal", "Periódica"],
                key=f"{key}_tipo_tasa",
            )

        with col_b:
            tasa = st.number_input(
                "Valor de la tasa (%)", min_value=0.0, max_value=1000.0,
                value=0.0, step=0.1, key=f"{key}_tasa",
            )

        # Siempre mostramos los campos de periodicidad y modalidad de la tasa para mayor claridad
        col_c, col_d = st.columns(2)

        if tipo_tasa == "Efectiva anual":
            with col_c:
                st.selectbox(
                    "Periodicidad de la tasa",
                    ["Anual"],
                    index=0,
                    disabled=True,
                    key=f"{key}_per_fija_ea"
                )
                periodicidad_tasa = "Anual"
            with col_d:
                modalidad = "Vencida"
                st.text_input("Modalidad", value="Vencida (fija)", disabled=True, key=f"{key}_mod_fija_ea")
            st.caption("La tasa efectiva anual es siempre anual y vencida.")
        else:
            etiqueta_per = (
                "Periodicidad de capitalización"
                if tipo_tasa == "Nominal"
                else "Periodicidad de la tasa"
            )

            with col_c:
                periodicidad_tasa = selector_periodicidad(
                    etiqueta_per, f"{key}_periodicidad_tasa"
                )

            with col_d:
                modalidad = st.selectbox(
                    "Modalidad",
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
    """Valida la tasa ingresada y la convierte automáticamente a la periodicidad de cálculo deseada."""
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
    with st.container(border=True):
        st.markdown("**Tiempo**")

        col_a, col_b = st.columns(2)

        with col_a:
            n = st.number_input(
                "Número de períodos", min_value=0.0, max_value=100000.0,
                value=1.0, step=1.0, key=f"{key}_n",
            )

        with col_b:
            periodicidad = selector_periodicidad(
                "Periodicidad del tiempo", f"{key}_periodicidad"
            )

    return n, periodicidad


def calcular_tiempo_resultado(n, p_tiempo, periodicidad_resultado):
    """Valida y convierte el tiempo a la periodicidad de cálculo."""
    validar_convertir_tiempo(n, p_tiempo, periodicidad_resultado)
    return convertir_tiempo(n, p_tiempo, periodicidad_resultado)


def mostrar_error(error):
    st.error(getattr(error, "mensaje", str(error)))


def verificar_resultado(valor):
    if not isinstance(valor, (int, float)) or valor != valor or abs(valor) == float("inf"):
        raise ValidacionError(
            "El resultado es demasiado grande para calcularse con estos "
            "datos. Reduce el valor, la tasa o el número de períodos."
        )


def boton_calcular(etiqueta, key):
    return st.button(etiqueta, key=key, type="primary", use_container_width=True)


def panel_resultado(columna, calcular, calculo):
    with columna:
        st.markdown("#### Resultado")

        if not calcular:
            st.info("Completa los datos de la izquierda y pulsa **Calcular**.")
            return

        try:
            titulo, valor, detalles = calculo()
        except ERRORES_CONTROLADOS as error:
            mostrar_error(error)
            return

        with st.container(border=True):
            st.metric(titulo, valor)
            for detalle in detalles:
                st.caption(detalle)


def columnas_pantalla():
    return st.columns([3, 2], gap="large")


# ---------------------------------------------------------
# BARRA LATERAL: NAVEGACIÓN
# ---------------------------------------------------------

with st.sidebar:
    st.title("Calculadora financiera")
    modulo = st.radio(
        "Módulo",
        ["Interés compuesto", "Conversiones", "Anualidades"],
        key="modulo",
    )
    st.divider()


# =========================================================
# MÓDULO 1: INTERÉS COMPUESTO
# =========================================================

def modulo_interes():
    with st.sidebar:
        operacion = st.selectbox(
            "Operación",
            ["Valor futuro", "Valor presente", "Tasa de interés", "Número de períodos"],
            key="operacion_interes",
        )

    st.header(f"Interés compuesto · {operacion}")
    izq, der = columnas_pantalla()

    if operacion == "Valor futuro":
        with izq:
            datos_tasa = ingresar_tasa("futuro")
            P = st.number_input("Valor presente (P)", min_value=0.01, max_value=1e12, value=100000.0, step=1000.0, key="futuro_P")
            n, periodicidad_tiempo = ingresar_tiempo("futuro")
            periodicidad_resultado = selector_periodicidad("Periodicidad para el cálculo", "futuro_periodicidad_resultado")
            calcular = boton_calcular("Calcular valor futuro", "btn_futuro")

        def calculo():
            tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)
            n_resultado = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_resultado)
            validar_valor_futuro(P, tasa_calculada, n_resultado)
            resultado = valor_futuro(P, tasa_calculada, n_resultado)
            verificar_resultado(resultado)
            return "Valor futuro", f"${resultado:,.2f}", [
                f"Tasa periódica vencida utilizada: {tasa_calculada:.6f} %",
                f"Número de períodos utilizados: {n_resultado:.6f}",
            ]

        panel_resultado(der, calcular, calculo)

    elif operacion == "Valor presente":
        with izq:
            datos_tasa = ingresar_tasa("presente")
            F = st.number_input("Valor futuro (F)", min_value=0.01, max_value=1e12, value=100000.0, step=1000.0, key="presente_F")
            n, periodicidad_tiempo = ingresar_tiempo("presente")
            periodicidad_resultado = selector_periodicidad("Periodicidad para el cálculo", "presente_periodicidad_resultado")
            calcular = boton_calcular("Calcular valor presente", "btn_presente")

        def calculo():
            tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)
            n_resultado = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_resultado)
            validar_valor_presente(F, tasa_calculada, n_resultado)
            resultado = valor_presente(F, tasa_calculada, n_resultado)
            verificar_resultado(resultado)
            return "Valor presente", f"${resultado:,.2f}", [
                f"Tasa periódica vencida utilizada: {tasa_calculada:.6f} %",
                f"Número de períodos utilizados: {n_resultado:.6f}",
            ]

        panel_resultado(der, calcular, calculo)

    elif operacion == "Tasa de interés":
        with izq:
            P = st.number_input("Valor presente (P)", min_value=0.01, max_value=1e12, value=100000.0, step=1000.0, key="interes_P")
            F = st.number_input("Valor futuro (F)", min_value=0.01, max_value=1e12, value=120000.0, step=1000.0, key="interes_F")
            n, periodicidad_tiempo = ingresar_tiempo("interes")
            periodicidad_resultado = selector_periodicidad("Periodicidad de la tasa que deseas obtener", "interes_periodicidad_resultado")
            calcular = boton_calcular("Calcular tasa", "btn_interes")

        def calculo():
            n_resultado = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_resultado)
            validar_valor_interes(F, P, n_resultado)
            tasa_calculada = valor_interes(F, P, n_resultado)
            verificar_resultado(tasa_calculada)
            return "Tasa periódica vencida", f"{tasa_calculada:.6f} %", [
                "Corresponde a la periodicidad seleccionada."
            ]

        panel_resultado(der, calcular, calculo)

    elif operacion == "Número de períodos":
        with izq:
            datos_tasa = ingresar_tasa("periodos")
            P = st.number_input("Valor presente (P)", min_value=0.01, max_value=1e12, value=100000.0, step=1000.0, key="periodos_P")
            F = st.number_input("Valor futuro (F)", min_value=0.01, max_value=1e12, value=120000.0, step=1000.0, key="periodos_F")
            periodicidad_resultado = selector_periodicidad("Periodicidad en la que deseas obtener los períodos", "periodos_periodicidad_resultado")
            calcular = boton_calcular("Calcular períodos", "btn_periodos")

        def calculo():
            tasa_calculada = calcular_tasa_resultado(datos_tasa, periodicidad_resultado)
            validar_valor_periodo(F, P, tasa_calculada)
            resultado = valor_periodo(F, P, tasa_calculada)
            verificar_resultado(resultado)
            return "Número de períodos", f"{resultado:.6f}", [
                f"Expresado en períodos de periodicidad {periodicidad_resultado.lower()}."
            ]

        panel_resultado(der, calcular, calculo)


# =========================================================
# MÓDULO 2: CONVERSIONES
# =========================================================

def modulo_conversiones():
    with st.sidebar:
        tipo_conversion = st.selectbox(
            "Operación",
            ["Convertir tasa", "Convertir tiempo"],
            key="tipo_conversion",
        )

    st.header(f"Conversiones · {tipo_conversion}")
    izq, der = columnas_pantalla()

    if tipo_conversion == "Convertir tasa":
        with izq:
            st.markdown("##### 1. Tasa que tienes")
            datos_tasa_conversion = ingresar_tasa("conversion")

            st.markdown("##### 2. Tasa que quieres obtener")

            with st.container(border=True):
                tipo_tasa_resultado = st.selectbox(
                    "Tipo de tasa de resultado",
                    ["Periódica", "Efectiva anual", "Nominal"],
                    key="conversion_tipo_tasa_resultado",
                )

                modalidad_resultado = "Vencida"

                if tipo_tasa_resultado == "Efectiva anual":
                    periodicidad_resultado = "Anual"
                    st.caption("La tasa calculada se expresará como Efectiva Anual (siempre vencida).")

                else:
                    col_a, col_b = st.columns(2)
                    etiqueta_per = (
                        "Periodicidad de capitalización"
                        if tipo_tasa_resultado == "Nominal"
                        else "Periodicidad de la tasa"
                    )
                    clave_per = (
                        "conversion_periodicidad_res_nominal"
                        if tipo_tasa_resultado == "Nominal"
                        else "conversion_periodicidad_resultado"
                    )
                    clave_mod = (
                        "conversion_modalidad_res_nominal"
                        if tipo_tasa_resultado == "Nominal"
                        else "conversion_modalidad_res_periodica"
                    )

                    with col_a:
                        periodicidad_resultado = selector_periodicidad(etiqueta_per, clave_per)

                    with col_b:
                        modalidad_resultado = st.selectbox(
                            "Modalidad", ["Vencida", "Anticipada"], key=clave_mod
                        )

            calcular = boton_calcular("Convertir tasa", "btn_conversion_tasa")

        def calculo():
            parametros = dict(
                tasa=datos_tasa_conversion["tasa"],
                tipo_tasa=datos_tasa_conversion["tipo_tasa"],
                periodicidad_tasa=datos_tasa_conversion["periodicidad_tasa"],
                modalidad=datos_tasa_conversion["modalidad"],
                tipo_resultado=tipo_tasa_resultado,
                periodicidad_resultado=periodicidad_resultado,
                modalidad_resultado=modalidad_resultado,
                es_indexada=datos_tasa_conversion["es_indexada"],
                tipo_indexado=datos_tasa_conversion["tipo_indexado"],
                tasa2=datos_tasa_conversion["tasa2"],
            )

            validar_convertir_tasa_completa(**parametros)
            resultado_final = convertir_tasa_completa(**parametros)
            verificar_resultado(resultado_final)

            if tipo_tasa_resultado == "Efectiva anual":
                etiqueta = "Tasa efectiva anual"
            else:
                etiqueta = (
                    f"Tasa {tipo_tasa_resultado.lower()} "
                    f"{periodicidad_resultado.lower()} "
                    f"{modalidad_resultado.lower()}"
                )

            return etiqueta, f"{resultado_final:.6f} %", []

        panel_resultado(der, calcular, calculo)

    elif tipo_conversion == "Convertir tiempo":
        with izq:
            n, periodicidad_tiempo = ingresar_tiempo("conversion_tiempo")
            periodicidad_resultado = selector_periodicidad("Periodicidad de resultado", "conversion_tiempo_resultado")
            calcular = boton_calcular("Convertir tiempo", "btn_conversion_tiempo")

        def calculo():
            resultado = calcular_tiempo_resultado(n, periodicidad_tiempo, periodicidad_resultado)
            return (
                "Tiempo convertido",
                f"{resultado:.6f}",
                [f"Períodos de periodicidad {periodicidad_resultado.lower()}."],
            )

        panel_resultado(der, calcular, calculo)


# =========================================================
# MÓDULO 3: ANUALIDADES
# =========================================================

FUNCIONES_ANUALIDAD = {
    "Vencida": {
        "presente": valor_presente_anualidad_vencida,
        "anualidad_presente": valor_anualidad_con_presente_vencida,
        "tiempo_presente": valor_tiempo_anualidad_vencida_con_presente,
        "validar_tiempo_presente": validar_calculo_tiempo_presente_vencida,
        "futuro": valor_futuro_anualidad_vencida,
        "anualidad_futuro": valor_anualidad_con_futuro_vencida,
        "tiempo_futuro": valor_tiempo_anualidad_vencida_con_futuro,
    },
    "Anticipada": {
        "presente": valor_presente_anualidad_anticipada,
        "anualidad_presente": valor_anualidad_con_presente_anticipada,
        "tiempo_presente": valor_tiempo_anualidad_anticipada_con_presente,
        "validar_tiempo_presente": validar_calculo_tiempo_presente_anticipada,
        "futuro": valor_futuro_anualidad_anticipada,
        "anualidad_futuro": valor_anualidad_con_futuro_anticipada,
        "tiempo_futuro": valor_tiempo_anualidad_anticipada_con_futuro,
    },
}

OPERACIONES_ANUALIDAD = [
    "Valor Presente (P)",
    "Anualidad (A) desde Presente",
    "Tiempo (n) desde Presente",
    "Valor Futuro (F)",
    "Anualidad (A) desde Futuro",
    "Tiempo (n) desde Futuro",
]


def seccion_anualidad(tipo, pref):
    f = FUNCIONES_ANUALIDAD[tipo]
    sufijo = " Anticipada" if tipo == "Anticipada" else ""
    sufijo_m = " Anticipado" if tipo == "Anticipada" else ""
    es_anticipada = (tipo == "Anticipada")

    with st.sidebar:
        operacion_anualidad = st.selectbox("Operación", OPERACIONES_ANUALIDAD, key=f"op_{pref}")

    st.header(f"Anualidad {tipo.lower()} · {operacion_anualidad}")
    izq, der = columnas_pantalla()

    if operacion_anualidad == "Valor Presente (P)":
        with izq:
            A = ingresar_monto("Valor de la anualidad (A)", 1000.0, f"{pref}_p_A")
            n, periodicidad_tiempo = ingresar_tiempo(f"{pref}_p_n")
            periodicidad_res = periodicidad_tiempo  # El período del tiempo manda y unifica el cálculo

            # El usuario ingresa la tasa y su respectiva periodicidad libremente:
            datos_tasa = ingresar_tasa(f"{pref}_p_tasa")

            calcular = boton_calcular(f"Calcular Valor Presente{sufijo_m}", f"btn_{pref}_p")

        def calculo():
            # Internamente la tasa se convierte de forma automática a la periodicidad de los pagos (periodicidad_res)
            tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
            n_int = validar_anualidad_con_periodos(A, "la anualidad (A)", tasa_calc, n)
            resultado = f["presente"](A, tasa_calc, n_int)
            verificar_resultado(resultado)
            return f"Valor Presente{sufijo_m} (P)", f"${resultado:,.2f}", [
                f"Periodicidad de pagos y cálculo: **{periodicidad_res}**",
                f"Tasa convertida internamente a periódica **{periodicidad_res.lower()} vencida**: **{tasa_calc:.6f}%**"
            ]

    elif operacion_anualidad == "Anualidad (A) desde Presente":
        with izq:
            P = ingresar_monto("Valor Presente (P)", 10000.0, f"{pref}_ap_P")
            n, periodicidad_tiempo = ingresar_tiempo(f"{pref}_ap_n")
            periodicidad_res = periodicidad_tiempo
            datos_tasa = ingresar_tasa(f"{pref}_ap_tasa")
            calcular = boton_calcular(f"Calcular Anualidad{sufijo} (A)", f"btn_{pref}_ap")

        def calculo():
            tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
            n_int = validar_anualidad_con_periodos(P, "el valor presente (P)", tasa_calc, n)
            resultado = f["anualidad_presente"](P, tasa_calc, n_int)
            verificar_resultado(resultado)
            return f"Anualidad{sufijo} (A)", f"${resultado:,.2f}", [
                f"Periodicidad de pagos y cálculo: **{periodicidad_res}**",
                f"Tasa convertida internamente: **{tasa_calc:.6f}%**"
            ]

    elif operacion_anualidad == "Tiempo (n) desde Presente":
        with izq:
            P = ingresar_monto("Valor Presente (P)", 10000.0, f"{pref}_tp_P")
            A = ingresar_monto("Valor de la anualidad (A)", 1000.0, f"{pref}_tp_A")
            periodicidad_res = selector_periodicidad("Periodicidad de los pagos y del cálculo", f"{pref}_tp_per")
            datos_tasa = ingresar_tasa(f"{pref}_tp_tasa")
            calcular = boton_calcular(f"Calcular Tiempo (n){sufijo_m}", f"btn_{pref}_tp")

        def calculo():
            tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
            f["validar_tiempo_presente"](P, tasa_calc, A)
            resultado = f["tiempo_presente"](P, tasa_calc, A)
            verificar_resultado(resultado)
            return "Número de períodos (n)", f"{resultado:.4f}", [
                f"Tasa adaptada a periodicidad **{periodicidad_res.lower()}**: **{tasa_calc:.6f}%**",
                f"Resultado expresado en períodos de periodicidad **{periodicidad_res.lower()}**."
            ]

    elif operacion_anualidad == "Valor Futuro (F)":
        with izq:
            A = ingresar_monto("Valor de la anualidad (A)", 1000.0, f"{pref}_f_A")
            n, periodicidad_tiempo = ingresar_tiempo(f"{pref}_f_n")
            periodicidad_res = periodicidad_tiempo
            datos_tasa = ingresar_tasa(f"{pref}_f_tasa")
            calcular = boton_calcular(f"Calcular Valor Futuro{sufijo_m}", f"btn_{pref}_f")

        def calculo():
            tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
            n_int = validar_anualidad_con_periodos(A, "la anualidad (A)", tasa_calc, n)
            resultado = f["futuro"](A, tasa_calc, n_int)
            verificar_resultado(resultado)
            return f"Valor Futuro{sufijo_m} (F)", f"${resultado:,.2f}", [
                f"Periodicidad de pagos y cálculo: **{periodicidad_res}**",
                f"Tasa convertida internamente: **{tasa_calc:.6f}%**"
            ]

    elif operacion_anualidad == "Anualidad (A) desde Futuro":
        with izq:
            F = ingresar_monto("Valor Futuro (F)", 15000.0, f"{pref}_af_F")
            n, periodicidad_tiempo = ingresar_tiempo(f"{pref}_af_n")
            periodicidad_res = periodicidad_tiempo
            datos_tasa = ingresar_tasa(f"{pref}_af_tasa")
            calcular = boton_calcular(f"Calcular Anualidad{sufijo} (A)", f"btn_{pref}_af")

        def calculo():
            tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
            n_int = validar_anualidad_con_periodos(F, "el valor futuro (F)", tasa_calc, n)
            resultado = f["anualidad_futuro"](F, tasa_calc, n_int)
            verificar_resultado(resultado)
            return f"Anualidad{sufijo} (A)", f"${resultado:,.2f}", [
                f"Periodicidad de pagos y cálculo: **{periodicidad_res}**",
                f"Tasa convertida internamente: **{tasa_calc:.6f}%**"
            ]

    else:  # Tiempo (n) desde Futuro
        with izq:
            F = ingresar_monto("Valor Futuro (F)", 15000.0, f"{pref}_tf_F")
            A = ingresar_monto("Valor de la anualidad (A)", 1000.0, f"{pref}_tf_A")
            periodicidad_res = selector_periodicidad("Periodicidad de los pagos y del cálculo", f"{pref}_tf_per")
            datos_tasa = ingresar_tasa(f"{pref}_tf_tasa")
            calcular = boton_calcular(f"Calcular Tiempo (n){sufijo_m}", f"btn_{pref}_tf")

        def calculo():
            tasa_calc = calcular_tasa_resultado(datos_tasa, periodicidad_res)
            validar_calculo_tiempo_futuro(F, tasa_calc, A, anticipada=es_anticipada)
            resultado = f["tiempo_futuro"](F, tasa_calc, A)
            verificar_resultado(resultado)
            return "Número de períodos (n)", f"{resultado:.4f}", [
                f"Tasa adaptada a periodicidad **{periodicidad_res.lower()}**: **{tasa_calc:.6f}%**",
                f"Resultado expresado en períodos de periodicidad **{periodicidad_res.lower()}**."
            ]

    panel_resultado(der, calcular, calculo)


def modulo_anualidades():
    with st.sidebar:
        sub_anualidad = st.radio(
            "Tipo de anualidad",
            ["Vencidas", "Anticipadas", "Perpetuas"],
            key="sub_anualidad",
        )

    if sub_anualidad == "Vencidas":
        seccion_anualidad("Vencida", "v")
    elif sub_anualidad == "Anticipadas":
        seccion_anualidad("Anticipada", "ant")
    else:
        st.header("Anualidad perpetua · Valor presente")
        izq, der = columnas_pantalla()

        with izq:
            A_perp = ingresar_monto("Valor de la anualidad perpetua (A)", 1000.0, "perp_A")
            periodicidad_perp = selector_periodicidad("Periodicidad de los pagos y del cálculo", "perp_per")
            datos_tasa_perp = ingresar_tasa("perp_tasa")
            calcular = boton_calcular("Calcular Valor Presente Perpetuo", "btn_perp")

        def calculo():
            tasa_calc_perp = calcular_tasa_resultado(datos_tasa_perp, periodicidad_perp)
            validar_calculo_perpetua(A_perp, tasa_calc_perp)
            resultado_perp = anualidad_perpetua(A_perp, tasa_calc_perp)
            verificar_resultado(resultado_perp)
            return "Valor Presente Perpetuo (P)", f"${resultado_perp:,.2f}", [
                f"Periodicidad de pagos y cálculo: **{periodicidad_perp}**",
                f"Tasa convertida internamente: **{tasa_calc_perp:.6f}%**"
            ]

        panel_resultado(der, calcular, calculo)


# ---------------------------------------------------------
# ENRUTADOR
# ---------------------------------------------------------

if modulo == "Interés compuesto":
    modulo_interes()
elif modulo == "Conversiones":
    modulo_conversiones()
else:
    modulo_anualidades()