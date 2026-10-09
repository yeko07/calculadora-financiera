import streamlit as st
from Utilidades.ValidacionError import ValidacionError
from Validaciones.Validacion_interes_compuesto import (
    validar_periodicidad,
    validar_valor_futuro,
    validar_valor_presente,
    validar_valor_interes,
    validar_valor_periodo
)
from Modulos.Interes_compuesto import (
    valor_futuro,
    valor_presente,
    valor_interes,
    valor_periodo
)

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Calculadora Financiera", page_icon="🧮", layout="centered")

st.title("Calculadora Financiera")

# Opciones globales para los menús desplegables de periodicidad
OPCIONES_TASA = ["Efectiva anual", "Mensual", "Bimestral", "Trimestral", "Semestral"]
OPCIONES_TIEMPO = ["Años", "Mensual", "Bimestral", "Trimestral", "Semestral"]

# Pestañas principales de la aplicación
tab_compuesto, tab_anualidades = st.tabs(["📈 Interés Compuesto", "🏦 Anualidades"])

with tab_compuesto:
    st.subheader("Selecciona la variable a calcular:")
    
    operacion = st.radio(
        "Incógnita:", 
        ["Valor Futuro (F)", "Valor Presente (P)", "Tasa de Interés (i)", "Número de Periodos (n)"],
        horizontal=True
    )
    
    st.markdown("---")

    # ==========================================
    # SECCIÓN 1: CALCULAR VALOR FUTURO (F)
    # ==========================================
    if operacion == "Valor Futuro (F)":
        st.markdown("### Calcular Valor Futuro (F)")
        
        # Selección de periodicidades en dos columnas paralelas
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            per_tasa = st.selectbox("Periodicidad de la Tasa:", OPCIONES_TASA, key="vf_per_tasa")
        with col_p2:
            per_tiempo = st.selectbox("Unidad del Tiempo (n):", OPCIONES_TIEMPO, key="vf_per_tiempo")

        col1, col2 = st.columns(2)
        with col1:
            P = st.number_input("Ingrese el Valor Presente (P):", min_value=0.0, step=1000.0, format="%.2f", key="vf_P")
            i = st.number_input("Ingrese la Tasa de Interés (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.2f", key="vf_i")
        with col2:
            n = st.number_input("Ingrese el Número de Periodos (n):", min_value=0, step=1, format="%d", key="vf_n")
            st.write("")
            btn_calcular = st.button("🧮 Calcular F", use_container_width=True, key="btn_vf")

        if btn_calcular:
            try:
                # 1. Mapeo de interfaz a lógica interna ("Efectiva anual" o "Periódica")
                tipo_tasa = "Efectiva anual" if per_tasa == "Efectiva anual" else "Periódica"
                
                # 2. Validación de consistencia de periodicidad y valores numéricos
                validar_periodicidad(tipo_tasa, per_tasa, per_tiempo)
                validar_valor_futuro(P, i, n)
                
                # 3. Cálculo y despliegue del resultado
                res = valor_futuro(P, i, n)
                st.metric(label="Resultado: Valor Futuro (F)", value=f"${res:,.2f}")
            except ValidacionError as e:
                st.error(f"⚠️ {e.mensaje}")

    # ==========================================
    # SECCIÓN 2: CALCULAR VALOR PRESENTE (P)
    # ==========================================
    elif operacion == "Valor Presente (P)":
        st.markdown("### Calcular Valor Presente (P)")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            per_tasa = st.selectbox("Periodicidad de la Tasa:", OPCIONES_TASA, key="vp_per_tasa")
        with col_p2:
            per_tiempo = st.selectbox("Unidad del Tiempo (n):", OPCIONES_TIEMPO, key="vp_per_tiempo")

        col1, col2 = st.columns(2)
        with col1:
            F = st.number_input("Ingrese el Valor Futuro (F):", min_value=0.0, step=1000.0, format="%.2f", key="vp_F")
            i = st.number_input("Ingrese la Tasa de Interés (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.2f", key="vp_i")
        with col2:
            n = st.number_input("Ingrese el Número de Periodos (n):", min_value=0, step=1, format="%d", key="vp_n")
            st.write("")
            btn_calcular = st.button("🧮 Calcular P", use_container_width=True, key="btn_vp")

        if btn_calcular:
            try:
                tipo_tasa = "Efectiva anual" if per_tasa == "Efectiva anual" else "Periódica"
                
                validar_periodicidad(tipo_tasa, per_tasa, per_tiempo)
                validar_valor_presente(F, i, n)
                
                res = valor_presente(F, i, n)
                st.metric(label="Resultado: Valor Presente (P)", value=f"${res:,.2f}")
            except ValidacionError as e:
                st.error(f"⚠️ {e.mensaje}")

    # ==========================================
    # SECCIÓN 3: CALCULAR TASA DE INTERÉS (i)
    # ==========================================
    elif operacion == "Tasa de Interés (i)":
        st.markdown("### Calcular Tasa de Interés (i)")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            per_tasa = st.selectbox("Periodicidad de la Tasa a calcular:", OPCIONES_TASA, key="i_per_tasa")
        with col_p2:
            per_tiempo = st.selectbox("Unidad del Tiempo (n):", OPCIONES_TIEMPO, key="i_per_tiempo")

        col1, col2 = st.columns(2)
        with col1:
            F = st.number_input("Ingrese el Valor Futuro (F):", min_value=0.0, step=1000.0, format="%.2f", key="i_F")
            P = st.number_input("Ingrese el Valor Presente (P):", min_value=0.0, step=1000.0, format="%.2f", key="i_P")
        with col2:
            n = st.number_input("Ingrese el Número de Periodos (n):", min_value=0, step=1, format="%d", key="i_n")
            st.write("")
            btn_calcular = st.button("🧮 Calcular i", use_container_width=True, key="btn_i")

        if btn_calcular:
            try:
                tipo_tasa = "Efectiva anual" if per_tasa == "Efectiva anual" else "Periódica"
                
                validar_periodicidad(tipo_tasa, per_tasa, per_tiempo)
                validar_valor_interes(F, P, n)
                
                res = valor_interes(F, P, n)
                # Si valor_interes ya retorna el valor en porcentaje (ej: 2.5), mostramos directo; si retorna decimal (0.025), usamos res * 100
                st.metric(label=f"Resultado: Tasa ({per_tasa})", value=f"{res:.4f} %")
            except ValidacionError as e:
                st.error(f"⚠️ {e.mensaje}")

    # ==========================================
    # SECCIÓN 4: CALCULAR NÚMERO DE PERIODOS (n)
    # ==========================================
    elif operacion == "Número de Periodos (n)":
        st.markdown("### Calcular Número de Periodos (n)")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            per_tasa = st.selectbox("Periodicidad de la Tasa:", OPCIONES_TASA, key="n_per_tasa")
        with col_p2:
            per_tiempo = st.selectbox("Unidad del Tiempo (n) a calcular:", OPCIONES_TIEMPO, key="n_per_tiempo")

        col1, col2 = st.columns(2)
        with col1:
            F = st.number_input("Ingrese el Valor Futuro (F):", min_value=0.0, step=1000.0, format="%.2f", key="n_F")
            P = st.number_input("Ingrese el Valor Presente (P):", min_value=0.0, step=1000.0, format="%.2f", key="n_P")
        with col2:
            i = st.number_input("Ingrese la Tasa de Interés (%):", min_value=0.0, max_value=100.0, step=0.1, format="%.2f", key="n_i")
            st.write("")
            btn_calcular = st.button("🧮 Calcular n", use_container_width=True, key="btn_n")

        if btn_calcular:
            try:
                tipo_tasa = "Efectiva anual" if per_tasa == "Efectiva anual" else "Periódica"
                
                validar_periodicidad(tipo_tasa, per_tasa, per_tiempo)
                validar_valor_periodo(P, F, i)
                
                res = valor_periodo(F, P, i)
                st.metric(label=f"Resultado: Periodos en ({per_tiempo})", value=f"{res:.2f} periodos")
            except ValidacionError as e:
                st.error(f"⚠️ {e.mensaje}")

# ==========================================
# PESTAÑA SECUNDARIA (FUTURA)
# ==========================================
with tab_anualidades:
    st.subheader("🏦 Módulo de Anualidades")
    st.info("Próximamente disponible.")