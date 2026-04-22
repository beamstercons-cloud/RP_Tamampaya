import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuración segura
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Falta la API Key en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Usamos un bloque try-except para capturar el error de 'NotFound'
try:
    # Intentamos con el modelo más estable y rápido
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    # Prueba rápida para verificar que el modelo responde
    model.generate_content("Hola", generation_config={"max_output_tokens": 1})
except Exception as e:
    st.warning(f"El modelo 'gemini-1.5-flash' dio error. Intentando con 'gemini-1.5-pro'...")
    try:
        model = genai.GenerativeModel('models/gemini-1.5-pro')
    except:
        st.error(f"No se pudo encontrar un modelo válido. Error técnico: {e}")
        st.stop()
# --- DIAGNÓSTICO ---
st.sidebar.write("### Diagnóstico de Conexión")
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    st.sidebar.write(f"Modelos detectados: {available_models}")
except Exception as e:
    st.sidebar.error(f"Error listando modelos: {e}")
    
# --- LISTA DE PROBLEMAS (Resumida para el ejemplo) ---
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

# --- FUNCIÓN PARA GENERAR PREGUNTA DE IA ---
def obtener_pregunta_profunda(problema_raiz, historial_respuestas):
    # El System Prompt define la personalidad de la IA
    system_instruction = f"""
    Eres un Consultor Senior de Ingeniería Hidráulica y Gestión Ambiental con 20 años de experiencia.
    Estás facilitando un análisis de '5 Porqués' para un equipo técnico en la Cuenca del Río Tamampaya, Bolivia.
    
    PROBLEMA ORIGINAL: {problema_raiz}
    
    HISTORIAL DE RESPUESTAS HASTA AHORA:
    {historial_respuestas}
    
    TU OBJETIVO: Analiza la última respuesta del usuario y genera una pregunta corta, técnica y punzante que empiece con '¿Por qué...?' 
    para profundizar más. No des soluciones, solo pregunta. 
    Enfócate en: fallas institucionales, procesos geofísicos, falta de datos, o factores socio-económicos.
    """
    
    response = model.generate_content(system_instruction)
    return response.text

# --- INTERFAZ STREAMLIT ---
st.title("🌊 Analizador de Causa Raíz - Cuenca Tamampaya")

if 'etapa' not in st.session_state:
    st.session_state.etapa = "seleccion"
    st.session_state.historial = []
    st.session_state.nivel = 1
    st.session_state.pregunta_actual = ""

if st.session_state.etapa == "seleccion":
    # (Misma lógica de selección de problemas que antes...)
    cod = st.selectbox("Selecciona el problema:", list(PROBLEMAS_INICIALES.keys()))
    if st.button("Comenzar"):
        st.session_state.cod_problema = cod
        st.session_state.desc_problema = PROBLEMAS_INICIALES[cod]['desc']
        # La primera pregunta es directa sobre el problema base
        st.session_state.pregunta_actual = f"¿Por qué ocurre este problema actualmente en la cuenca?"
        st.session_state.etapa = "analisis"
        st.rerun()

elif st.session_state.etapa == "analisis" and st.session_state.nivel <= 5:
    st.subheader(f"Nivel {st.session_state.nivel} de profundidad")
    st.info(f"**Pregunta de la IA:** {st.session_state.pregunta_actual}")
    
    respuesta = st.text_area("Tu respuesta técnica:", key=f"input_{st.session_state.nivel}")
    
    if st.button("Analizar y Continuar"):
        if respuesta:
            # Guardar en historial
            st.session_state.historial.append({
                "Nivel": st.session_state.nivel,
                "Pregunta": st.session_state.pregunta_actual,
                "Respuesta": respuesta
            })
            
            # Si no hemos llegado al nivel 5, pedirle a Gemini la siguiente pregunta
            if st.session_state.nivel < 5:
                with st.spinner("Gemini está analizando tu respuesta..."):
                    historial_texto = "\n".join([f"P: {h['Pregunta']} | R: {h['Respuesta']}" for h in st.session_state.historial])
                    st.session_state.pregunta_actual = obtener_pregunta_profunda(st.session_state.desc_problema, historial_texto)
                
            st.session_state.nivel += 1
            st.rerun()
        else:
            st.warning("Escribe una respuesta para continuar.")

else:
    # --- RESULTADOS FINALES ---
    st.success("🎯 Análisis finalizado. Aquí tienes la tabla de causa raíz:")
    df = pd.DataFrame(st.session_state.historial)
    st.table(df)
    
    # Exportar a CSV para tus reportes
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Informe", csv, "causa_raiz.csv", "text/csv")
