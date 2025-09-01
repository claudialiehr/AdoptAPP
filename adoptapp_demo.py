import streamlit as st
from datetime import datetime
import json

# --------------------------------------
# Configuración básica
# --------------------------------------
st.set_page_config(page_title="AdoptAPP - Evaluación de Adoptantes", layout="centered")
st.title("🐾 AdoptAPP")
st.subheader("Sistema de preevaluación para solicitudes de adopción")
st.markdown(
    "Completa el formulario. El sistema mostrará una evaluación preliminar "
    "y, si lo permites, enviaremos un **resumen** a la protectora."
)

# Leemos la URL del webhook desde los secrets (en Streamlit Cloud ya lo guardaste)
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", None)
PROTECTORA_EMAIL = st.secrets.get("PROTECTORA_EMAIL", None)  # opcional

# --------------------------------------
# Funciones auxiliares
# --------------------------------------
def clasificar_adoptante(edad, tiempo_libre, redes_seguridad, experiencia, tipo_vivienda):
    """
    Devuelve (puntos, etiqueta, color)
    Reglas simples y transparentes.
    """
    puntos = 0
    if edad >= 22: puntos += 1
    if tiempo_libre in ["3-5 horas", ">5 horas"]: puntos += 1
    if redes_seguridad == "Sí": puntos += 1
    if experiencia == "Alta":
       puntos += 2
    elif experiencia == "Media":
       puntos += 1
# "Baja" suma 0
    if tipo_vivienda in ["Piso", "Ático", "Casa/Chalet", "Vivienda Compartida"]: puntos += 1
    if vives_alquiler == "Sí" and permiso_mascotas == "No": puntos -= 1

    if puntos >= 4:
        return puntos, "APTO", "success"
    elif puntos >= 2:
        return puntos, "INTERMEDIO", "warning"
    else:
        return puntos, "NO APTO", "error"

def enviar_resumen_por_webhook(payload: dict, webhook_url: str):
    """Envía el resumen al webhook (Zapier/Make). Devuelve (ok, mensaje)."""
    if not webhook_url:
        return False, "No hay WEBHOOK_URL configurado (no se envía)."
    try:
        import urllib.request
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            if 200 <= code < 300:
                return True, f"Enviado correctamente (HTTP {code})."
            return False, f"Error HTTP {code} al enviar."
    except Exception as e:
        return False, f"No se pudo enviar: {e}"

# --------------------------------------
# Formulario
# --------------------------------------
with st.form("adoption_form"):
    nombre = st.text_input("👤 Nombre completo del adoptante")
    telefono = st.text_input("📱 Teléfono de contacto (móvil)")
    nombre_animal = st.text_input("🐶 Nombre del animal que quieres adoptar")

    edad = st.slider("Edad", 18, 80, 30)
    genero = st.selectbox("Género", ["Mujer", "Hombre", "Otro"])
    ubicacion = st.text_input("Ciudad / Provincia")
    tipo_vivienda = st.selectbox("Tipo de vivienda", ["Piso", "Casa", "Ático", "Otro"])

    # ❓ Pregunta condicional
    vives_alquiler = st.radio("🏠 ¿Vives de alquiler?", ["Sí", "No"])
    permiso_mascotas = None
    if vives_alquiler == "Sí":
        permiso_mascotas = st.radio(
            "¿Tienes permiso para tener mascotas del/de la caser@?",
            ["Sí", "No"]
        )

    tiempo_libre = st.selectbox(
        "¿Cuánto tiempo tienes al día para el animal?",
        ["<1 hora", "1-3 horas", "3-5 horas", ">5 horas"]
    )
    redes_seguridad = st.radio(
        "¿Estás dispuesto/a a instalar redes de seguridad en ventanas/balcones?",
        ["Sí", "No", "No aplica (no tengo gatos)"]
    )
    experiencia = st.selectbox(
        "¿Cuál es tu experiencia con animales de compañía?",
        ["Baja", "Media", "Alta"]
    )

    consent = st.checkbox(
        "Autorizo a enviar mi solicitud a la protectora para su evaluación",
        value=True
    )

    submit = st.form_submit_button("Enviar solicitud")

# --------------------------------------
# Resultado y envío
# --------------------------------------
if submit:
    # 1) Clasificación
    puntos, etiqueta, color = clasificar_adoptante(edad, tiempo_libre, redes_seguridad, experiencia, tipo_vivienda)

    st.markdown("### 🧠 Evaluación del sistema:")
    if color == "success":
        st.success("✅ Alta probabilidad de ser un adoptante responsable. Se recomienda avanzar con la entrevista.")
    elif color == "warning":
        st.warning("⚠️ Perfil intermedio. Requiere evaluación manual adicional.")
    else:
        st.error("❌ Perfil con bajo encaje inicial. Se recomienda revisar motivaciones y condiciones.")

    # 2) Resumen claro (lo ve la persona y se puede enviar)
    resumen = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "etiqueta": etiqueta,
    "puntos": puntos,
    "nombre": nombre,
    "telefono": telefono,
    "nombre_animal": nombre_animal,
    "edad": edad,
    "genero": genero,
    "ubicacion": ubicacion,
    "tipo_vivienda": tipo_vivienda,
    "vives_alquiler": vives_alquiler,
    "permiso_mascotas": permiso_mascotas,
    "tiempo_libre": tiempo_libre,
    "redes_seguridad": redes_seguridad,
    "experiencia": experiencia,
    "destinatario_protectora": PROTECTORA_EMAIL,
    "origen": "AdoptAPP (Streamlit)"

}

    st.markdown("### 📨 Resumen para la protectora")
    st.json(resumen)

    # 3) Envío por webhook (si hay consentimiento y está configurado)
    if consent:
        ok, msg = enviar_resumen_por_webhook(resumen, WEBHOOK_URL)
        if ok:
            st.info("Resumen enviado a la protectora. " + msg)
        else:
            st.info("No se pudo enviar automáticamente. " + msg + " (Puedes copiar el resumen manualmente).")
    else:
        st.info("No se enviará el resumen porque no diste consentimiento.")

    st.markdown("---")
    st.markdown("📝 **Nota:** Esta evaluación es preliminar y no sustituye el criterio del personal de la protectora.")
