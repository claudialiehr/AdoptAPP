import streamlit as st
from datetime import datetime
import json

# -------------------------------
# Configuración inicial
# -------------------------------
st.set_page_config(
    page_title="AdoptAPP - ¡Adopta no compres!",
    layout="centered",
    initial_sidebar_state="collapsed"  # 👉 Sidebar cerrada por defecto (icono ☰ arriba a la izquierda)
)

# -------------------------------
# Menú lateral (se abre con ☰)
# -------------------------------
with st.sidebar:
    st.title("☰ Menú")
    pagina = st.radio("Navegación", [
        "Formulario de adopción",
        "Animales en adopción",
        "Tips de alimentación",
        "Historias de adopción",
        "Ley de Bienestar Animal"
    ])

# -------------------------------
# Funciones auxiliares
# -------------------------------
def clasificar_adoptante(
    edad, tiempo_libre, redes_seguridad, experiencia, tipo_vivienda, permiso_mascotas
):
    if permiso_mascotas == "No":
        return -1, "NO APTO", "error"

    puntos = 0
    # Edad
    if edad < 25:
        puntos += 1
    elif 25 <= edad <= 44:
        puntos += 2
    elif 45 <= edad <= 60:
        puntos += 1
    else:
        puntos -= 1
    # Tiempo libre
    if tiempo_libre == "2-5 horas":
        puntos += 1
    elif tiempo_libre == ">5 horas":
        puntos += 2
    # Seguridad
    if redes_seguridad == "Sí":
        puntos += 2
    # Experiencia
    if experiencia == "Media":
        puntos += 1
    elif experiencia == "Alta":
        puntos += 2
    # Vivienda
    if tipo_vivienda in ["Piso", "Casa", "Casa/Chalet"]:
        puntos += 2
    elif tipo_vivienda == "Ático":
        puntos += 1

    # Umbrales
    if puntos >= 7:
        return puntos, "APTO", "success"
    elif 4 <= puntos <= 6:
        return puntos, "INTERMEDIO", "warning"
    else:
        return puntos, "NO APTO", "error"


def enviar_resumen_por_webhook(payload: dict, webhook_url: str):
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


WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", None)
PROTECTORA_EMAIL = st.secrets.get("PROTECTORA_EMAIL", None)

# -------------------------------
# Página 1: Formulario
# -------------------------------
if pagina == "Formulario de adopción":
    st.title("🐾 AdoptAPP")
    st.subheader("Cuestionario de preevaluación")
    st.markdown("Completa el formulario. Revisaremos tu solicitud a la mayor brevedad.")

    with st.form("adoption_form"):
        nombre = st.text_input("👤 Nombre completo del adoptante")
        telefono = st.text_input("📱 Teléfono de contacto (móvil)")
        nombre_animal = st.text_input("🐶😺 Nombre del animal que quieres adoptar")

        edad = st.slider("Edad", 18, 80, 30)
        genero = st.selectbox("Género", ["Mujer", "Hombre", "No me representa"])
        ubicacion = st.text_input("Ciudad / Provincia")
        tipo_vivienda = st.selectbox("Tipo de vivienda", ["Piso", "Casa", "Ático", "Vivienda Compartida"])

        permiso_mascotas = st.radio(
            "🏠 ¿Vives de alquiler y tienes permiso para tener mascotas?",
            ["Sí", "No", "No aplica (vivienda propia)"]
        )

        tiempo_libre = st.selectbox(
            "⏰ ¿Cuánto tiempo tienes al día para el animal?",
            ["1-2 horas", "2-5 horas", ">5 horas"]
        )

        redes_seguridad = st.radio(
            "🔒 ¿Instalarías redes de seguridad en ventanas/balcones para el gato?",
            ["Sí", "No", "No aplica"]
        )

        experiencia = st.selectbox(
            "🐾 ¿Cuál es tu experiencia con animales de compañía?",
            ["Baja", "Media", "Alta"]
        )

        consent = st.checkbox(
            "Autorizo a enviar mi solicitud a la protectora para su evaluación",
            value=False
        )

        submit = st.form_submit_button("Enviar solicitud")

    if submit:
        puntos, etiqueta, color = clasificar_adoptante(
            edad, tiempo_libre, redes_seguridad, experiencia, tipo_vivienda, permiso_mascotas
        )

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
            "permiso_mascotas": permiso_mascotas,
            "tiempo_libre": tiempo_libre,
            "redes_seguridad": redes_seguridad,
            "experiencia": experiencia,
            "destinatario_protectora": PROTECTORA_EMAIL,
            "origen": "AdoptAPP (Streamlit)"
        }

        if consent:
            ok, msg = enviar_resumen_por_webhook(resumen, WEBHOOK_URL)
            if ok:
                st.success("✅ Tu solicitud se ha enviado correctamente a la protectora.")
            else:
                st.error("⚠️ No se pudo enviar automáticamente. Intenta más tarde.")
        else:
            st.info("ℹ️ No se enviará la solicitud porque no diste consentimiento.")

    st.caption("Al enviar confirmas que los datos son veraces. El envío a la protectora solo se realizará si otorgas tu consentimiento.")
    with st.expander("ℹ️ Información sobre protección de datos (RGPD)"):
        st.markdown("""
**Responsable:** [Nombre de la protectora]  
**Finalidad:** Gestionar la preevaluación de solicitudes de adopción.  
**Base jurídica:** Consentimiento de la persona interesada (art. 6.1.a RGPD).  
**Destinatarios:** La protectora indicada; no se realizan cesiones a terceros salvo obligación legal.  
**Conservación:** Durante el tiempo necesario para la tramitación de la solicitud y los plazos legales aplicables.  
**Derechos:** Acceso, rectificación, supresión, oposición, limitación y portabilidad.  
**Contacto:** [email de la protectora]  
**Información adicional:** No recopilamos tu IP ni datos de navegación en este formulario más allá de lo estrictamente necesario para el envío.
""")

# -------------------------------
# Página 2: Animales
# -------------------------------
elif pagina == "Animales en adopción":
    st.title("🐕 Animales en adopción")
    st.info("Aquí puedes mostrar un listado con fotos y fichas de animales en adopción.")
    st.image("https://place-puppy.com/300x300", caption="Luna – 2 años, Protectora A")
    st.image("https://placekitten.com/300/300", caption="Michi – 1 año, Protectora B")

# -------------------------------
# Página 3: Tips
# -------------------------------
elif pagina == "Tips de alimentación":
    st.title("🍖 Tips de alimentación y cuidados")
    st.markdown("- [Guía de piensos](https://example.com)")
    st.markdown("- [Tiendas recomendadas](https://example.com)")

# -------------------------------
# Página 4: Historias
# -------------------------------
elif pagina == "Historias de adopción":
    st.title("📖 Historias de adopciones exitosas")
    st.success("“Luna fue adoptada en 2023 y ahora vive feliz con su nueva familia.”")
    st.image("https://place-puppy.com/400x300")

# -------------------------------
# Página 5: Ley
# -------------------------------
elif pagina == "Ley de Bienestar Animal":
    st.title("⚖️ Ley de Bienestar Animal")
    st.markdown("Resumen de los puntos clave de la ley...")
    st.markdown("[Consulta el texto completo en el BOE](https://www.boe.es)")
