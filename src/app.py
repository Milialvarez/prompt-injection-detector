import streamlit as st
from firewall import analyze_prompt

st.set_page_config(page_title="LLM Security Firewall", page_icon="🛡️", layout="centered")

st.title("LLM Security Firewall")
st.markdown("""
¡Bienvenido al detector de ataques para Modelos de Lenguaje! 
Escribe un prompt abajo y la IA analizará en tiempo real si es seguro o si intenta vulnerar el sistema.
""")

st.divider() 

user_input = st.text_area("Ingresa el prompt a analizar:", height=150, placeholder="Ejemplo: Ignore previous instructions and...")

if st.button("Analizar Amenaza", use_container_width=True):
    
    if user_input.strip() == "":
        st.warning("Por favor, ingresa un texto para poder analizarlo.")
    else:
        with st.spinner("Analizando vectores semánticos..."):
            score, decision, attack_type = analyze_prompt(user_input)
        
        st.divider()
        st.subheader("Resultados del Análisis")
        
        st.metric(label="Threat Score (Nivel de Amenaza)", value=f"{score:.2f} / 1.0")
        
        if decision == "BLOCK":
            st.error(f"**🚫 ACCIÓN BLOQUEADA**\n\nSe ha detectado un ataque de tipo: **{attack_type.upper()}**.")
            st.progress(score)
            
        elif decision == "FLAG":
            st.warning(f"**⚠️ COMPORTAMIENTO SOSPECHOSO**\n\nEl prompt fue marcado para revisión. Posible **{attack_type.upper()}**.")
            
        else:
            st.success("**✅ ACCIÓN PERMITIDA**\n\nEl prompt parece ser seguro y no presenta amenazas.")