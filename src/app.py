import streamlit as st
from firewall import analyze_prompt
from supabase import create_client, Client
import pandas as pd

st.set_page_config(page_title="LLM Security Firewall", page_icon="🛡️", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.sidebar.title("Navegación")
modo = st.sidebar.radio("Selecciona la vista:", ["🛡️ Firewall Público", "🔐 Panel de Admin"])

# ==========================================
# Public firewall for normal users
# ==========================================
if modo == "🛡️ Firewall Público":
    st.title("🛡️ LLM Security Firewall")
    st.markdown("Escribe un prompt abajo y nuestra IA analizará en tiempo real si es seguro o si intenta vulnerar el sistema.")
    st.divider()

    user_input = st.text_area("Ingresa el prompt a analizar:", height=150)

    if st.button("🔍 Analizar Amenaza", use_container_width=True):
        if user_input.strip() == "":
            st.warning("Por favor, ingresa un texto para poder analizarlo.")
        else:
            with st.spinner("Analizando vectores semánticos..."):
                score, decision, attack_type = analyze_prompt(user_input)
                
                try:
                    supabase.table("prompt_logs").insert({
                        "prompt_text": user_input,
                        "predicted_class": attack_type,
                        "threat_score": score
                    }).execute()
                except Exception as e:
                    print(f"Error guardando en BD: {e}")

            st.divider()
            st.subheader("Resultados del Análisis")
            st.metric(label="Threat Score (Nivel de Amenaza)", value=f"{score:.2f} / 1.0")
            
            if decision == "BLOCK":
                st.error(f"**🚫 ACCIÓN BLOQUEADA**\n\nSe ha detectado un ataque de tipo: **{attack_type.upper()}**.")
                st.progress(score)
            elif decision == "FLAG":
                st.warning(f"**⚠️ COMPORTAMIENTO SOSPECHOSO**\n\nPosible **{attack_type.upper()}**.")
            else:
                st.success("**✅ ACCIÓN PERMITIDA**\n\nEl prompt parece ser seguro y no presenta amenazas.")

# ==========================================
# Hidden admin panel: this allows me (Mili) 
# to review AI conclussions and fix them when 
# they are incorrect, so the model can learn 
# and train itself from that
# ==========================================
elif modo == "Panel de Admin":
    st.title("Panel de Revisión (Human-in-the-Loop)")
    
    password = st.text_input("Ingresa la contraseña de administrador:", type="password")
    
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.success("¡Acceso concedido!")
        st.divider()
        
        try:
            response = supabase.table("prompt_logs").select("*").eq("is_reviewed", False).execute()
            logs_pendientes = response.data
            
            if not logs_pendientes:
                st.info("🎉 ¡Todo al día! No hay nuevos prompts para revisar.")
            else:
                st.write(f"Tienes **{len(logs_pendientes)}** prompts pendientes de validación:")
                
                log = logs_pendientes[0]
                
                st.markdown("### 🔍 Analizando Prompt ID: " + str(log['id']))
                st.code(log['prompt_text'], language="text")
                st.write(f"**La IA dijo que era:** `{log['predicted_class']}` (Score: {log['threat_score']:.2f})")
                
                etiquetas_posibles = ["safe", "jailbreak", "data_exfiltration", "obfuscation", "prompt_injection"]
                
                indice_prediccion = etiquetas_posibles.index(log['predicted_class']) if log['predicted_class'] in etiquetas_posibles else 0
                
                etiqueta_correcta = st.selectbox("¿Cuál es la etiqueta real?", etiquetas_posibles, index=indice_prediccion)
                
                if st.button("Validar y Guardar", type="primary"):
                    supabase.table("prompt_logs").update({
                        "is_reviewed": True,
                        "human_label": etiqueta_correcta
                    }).eq("id", log['id']).execute()
                    
                    st.success("¡Guardado! Recarga la página para ver el siguiente.")
                    st.rerun() 
                    
        except Exception as e:
            st.error(f"Error al conectar con la base de datos: {e}")
            
    elif password != "":
        st.error("Contraseña incorrecta.")