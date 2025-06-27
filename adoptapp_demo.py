
import streamlit as st

st.set_page_config(page_title="AdoptAPP - Evaluación de Adoptantes", layout="centered")

st.title("🐾 AdoptAPP")
st.subheader("Sistema de preevaluación para solicitudes de adopción")

st.markdown("Por favor, completa el siguiente formulario. Nuestro sistema inteligente analizará la solicitud y mostrará una evaluación preliminar.")

# Formulario
with st.form("adoption_form"):
    nombre = st.text_input("Nombre completo")
    edad = st.slider("Edad", 18, 80, 30)
    genero = st.selectbox("Género", ["Mujer", "Hombre", "Otro"])
    ubicacion = st.text_input("Ciudad / Provincia")
    tipo_vivienda = st.selectbox("Tipo de vivienda", ["Piso", "Casa", "Ático", "Otro"])
    tiempo_libre = st.selectbox("¿Cuánto tiempo tienes al día para el animal?", ["<1 hora", "1-3 horas", "3-5 horas", ">5 horas"])
    redes_seguridad = st.radio("¿Estás dispuesto/a a instalar redes de seguridad en ventanas/balcones?", ["Sí", "No", "No aplica (no tengo gatos)"])
    experiencia = st.radio("¿Has tenido animales anteriormente?", ["Sí", "No"])

    submit = st.form_submit_button("Enviar solicitud")

if submit:
    # Simulación de lógica de evaluación simple
    puntos = 0
    if edad > 21: puntos += 1
    if tiempo_libre in ["3-5 horas", ">5 horas"]: puntos += 1
    if redes_seguridad == "Sí": puntos += 1
    if experiencia == "Sí": puntos += 1
    if tipo_vivienda in ["Casa", "Ático"]: puntos += 1

    st.markdown("### 🧠 Evaluación del sistema:")
    if puntos >= 4:
        st.success("✅ Alta probabilidad de ser un adoptante responsable. Se recomienda avanzar con la entrevista.")
    elif puntos >= 2:
        st.warning("⚠️ Perfil intermedio. Requiere evaluación manual adicional.")
    else:
        st.error("❌ Perfil con bajo encaje inicial. Se recomienda revisar motivaciones y condiciones.")

    st.markdown("---")
    st.markdown("📝 **Nota:** Esta evaluación es preliminar y no sustituye el criterio del personal de la protectora.")
