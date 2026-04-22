import streamlit as st
import pandas as pd

# 1. Diccionario de problemas iniciales (tu lista técnica)
PROBLEMAS_INICIALES = {
    "P1": {"titulo": "Contaminación minera y mercurio", "desc": "Proliferación de cooperativas auríferas que alteran cauces y contaminan con mercurio."},
    "P2": {"titulo": "Deforestación y chaqueos", "desc": "Pérdida de cobertura boscosa y zonas de recarga por quemas no reguladas."},
    "P3": {"titulo": "Monocultivo y agroquímicos", "desc": "Expansión de frontera agrícola (coca) con uso excesivo de químicos y erosión."},
    "P4": {"titulo": "Degradación de fertilidad del suelo", "desc": "Pérdida severa de carbono orgánico por malas prácticas agrícolas."},
    "P5": {"titulo": "Erosión extrema en cabeceras", "desc": "Erosión hídrica superior a 1,200 t/ha/año en zonas de alta pendiente."},
    "P6": {"titulo": "Ineficiencia en Calidad de Agua Potable", "desc": "Sistemas incapaces de cumplir normas de potabilidad de forma continua."},
    "P7": {"titulo": "Déficit en Saneamiento y Aguas Servidas", "desc": "Descarga cruda de excretas al Río Tamampaya por falta de PTAR."},
    "P8": {"titulo": "Gestión Deficiente de Residuos Sólidos", "desc": "Márgenes de ríos convertidos en basurales y focos de infección."},
    "P9": {"titulo": "Vulnerabilidad a sequías", "desc": "Reducción de caudales base y desecación de vertientes por cambio climático."},
    "P10": {"titulo": "Inestabilidad de laderas", "desc": "Riesgos de deslizamientos y mazamorras por apertura de caminos y pendientes."},
    "P11": {"titulo": "Debilidad institucional municipal", "desc": "Presupuestos insuficientes y falta de personal técnico especializado."},
    "P12": {"titulo": "Deficiente administración de sistemas de agua", "desc": "Vulnerabilidad técnica en Comités de Agua y redes obsoletas."},
    "P13": {"titulo": "Vacío en fiscalización normativa", "desc": "Incapacidad para sancionar actividades destructivas (minería/chaqueos)."},
    "P14": {"titulo": "Conflictos sociales por uso del agua", "desc": "Competencia por el recurso entre consumo, minería y agricultura."},
    "P15": {"titulo": "Vulnerabilidad por Dependencia del Monocultivo", "desc": "Especialización en hoja de coca que genera inseguridad alimentaria."},
    "P16": {"titulo": "Limitada Capacidad de Agregación de Valor", "desc": "Falta de infraestructura para transformar productos primarios."},
    "P17": {"titulo": "Acceso limitado a Ecoturismo", "desc": "Falta de políticas de conservación y caminos en mal estado."}
}

# Configuración de Streamlit
st.set_page_config(page_title="Analizador Técnico - 5 Whys", layout="wide")

# Inicialización de estados
if 'etapa' not in st.session_state:
    st.session_state.etapa = "seleccion"
    st.session_state.historial = []
    st.session_state.nivel = 1

# --- INTERFAZ DE SELECCIÓN ---
if st.session_state.etapa == "seleccion":
    st.header("Selector de Problemas Estratégicos")
    st.info("Selecciona el problema identificado para profundizar en su causa raíz.")
    
    usuario = st.text_input("Nombre del evaluador / Técnico:")
    cod_problema = st.selectbox("Código del Problema:", list(PROBLEMAS_INICIALES.keys()))
    
    if cod_problema:
        st.write(f"**Descripción:** {PROBLEMAS_INICIALES[cod_problema]['desc']}")

    if st.button("Iniciar Análisis Profundo") and usuario:
        st.session_state.usuario = usuario
        st.session_state.cod_problema = cod_problema
        st.session_state.desc_problema = PROBLEMAS_INICIALES[cod_problema]['desc']
        st.session_state.etapa = "analisis"
        st.rerun()

# --- INTERFAZ DE ANÁLISIS (CICLO DE IA) ---
elif st.session_state.etapa == "analisis" and st.session_state.nivel <= 5:
    st.subheader(f"Analizando: {st.session_state.cod_problema} - {PROBLEMAS_INICIALES[st.session_state.cod_problema]['titulo']}")
    
    # Texto de referencia para la pregunta
    contexto_anterior = st.session_state.desc_problema if st.session_state.nivel == 1 else st.session_state.historial[-1]['Respuesta']
    
    st.write(f"**Contexto actual:** {contexto_anterior}")
    
    # Aquí simularíamos la llamada a la IA (OpenAI/Gemini)
    # El prompt diría: "Como experto en ingeniería, pregunta por qué ocurre {contexto_anterior}"
    pregunta_ia = f"¿Por qué crees que ocurre o se mantiene esta situación: '{contexto_anterior}'?"
    
    respuesta = st.text_area(f"Nivel {st.session_state.nivel}: {pregunta_ia}")

    if st.button(f"Confirmar Nivel {st.session_state.nivel}"):
        if respuesta:
            st.session_state.historial.append({
                "Nivel": f"Porqué {st.session_state.nivel}",
                "Pregunta IA": pregunta_ia,
                "Respuesta": respuesta
            })
            st.session_state.nivel += 1
            st.rerun()
        else:
            st.warning("Es necesario registrar una respuesta para profundizar.")

# --- RESULTADOS FINALES ---
else:
    st.success("Análisis de Causa Raíz Completado")
    st.write(f"**Evaluador:** {st.session_state.usuario}")
    st.write(f"**Problema Base:** {st.session_state.cod_problema}")
    
    df_resultados = pd.DataFrame(st.session_state.historial)
    st.table(df_resultados)
    
    # Botón para descargar resultados (útil para informes técnicos)
    csv = df_resultados.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Informe (CSV)", csv, f"analisis_{st.session_state.cod_problema}.csv", "text/csv")
    
    if st.button("Nuevo Análisis"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
