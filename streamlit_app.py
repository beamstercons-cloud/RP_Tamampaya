import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DE GEMINI ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') # Versión rápida e inteligente
except:
    st.error("Error: No se encontró la API Key de Gemini en los Secrets.")

# --- LISTA DE PROBLEMAS (Resumida para el ejemplo) ---
PROBLEMAS_INICIALES = {
    "P1": {"titulo": "Contaminación minera y mercurio", "desc": "Proliferación de cooperativas auríferas que alteran cauces y contaminan con mercurio."},
    # ... (Aquí irían los 17 problemas que pasaste anteriormente)
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
