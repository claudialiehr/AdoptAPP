import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json



# -------------------------------
# Config básica (siempre lo primero)
# -------------------------------
st.set_page_config(page_title="AdoptAPP - ¡Adopta no compres!",
                   layout="centered",
                   initial_sidebar_state="collapsed")

menu_html = """
<style>
.menu-container { position: relative; display: inline-block; }
.menu-button { font-size: 28px; cursor: pointer; user-select: none; }
.menu-content { display: none; position: absolute; top: 40px; left: 0;
  background: white; border: 1px solid #ddd; border-radius: 8px;
  min-width: 200px; box-shadow: 0px 8px 16px rgba(0,0,0,0.15); z-index: 1000; }
.menu-content a { display: block; padding: 10px; color: black; text-decoration: none; }
.menu-content a:hover { background-color: #f0f0f0; }
</style>
<div class="menu-container">
  <div class="menu-button" onclick="toggleMenu()">☰</div>
  <div class="menu-content" id="menu">
    <a href="#formulario">Formulario de adopción</a>
    <a href="#animales">Animales en adopción</a>
    <a href="#tips">Tips de alimentación</a>
    <a href="#historias">Historias de adopción</a>
    <a href="#ley">Ley de Bienestar Animal</a>
  </div>
</div>
<script>
function toggleMenu() {
  var x = document.getElementById("menu");
  if (x.style.display === "block") {
    x.style.display = "none";
  } else {
    x.style.display = "block";
  }
}
</script>
"""
components.html(menu_html, height=200)

# 2) Inyecta CSS para que la sidebar sea un rail que se expande al hover
st.markdown("""
<style>
/* Sidebar en modo rail estrecho */
section[data-testid="stSidebar"] {
  width: 64px !important;
  min-width: 64px !important;
  transition: width 0.25s ease-in-out;
  overflow-x: hidden;
  border-right: 1px solid #eee;
}

/* Al pasar el ratón, expandir */
section[data-testid="stSidebar"]:hover {
  width: 280px !important;
  min-width: 280px !important;
}

/* Opcional: compactar el contenido interno cuando está colapsado */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
  padding-top: 0.5rem;
}
section[data-testid="stSidebar"] .block-container {
  padding-top: 0.75rem;
}

/* Hacer que las etiquetas del radio no se corten al expandir */
section[data-testid="stSidebar"] label {
  white-space: nowrap;
}

/* Quitar un poco de padding al radio para que quepa bien en el rail */
section[data-testid="stSidebar"] [role="radiogroup"] > div {
  padding: .25rem .5rem;
}
</style>
""", unsafe_allow_html=True)

# Secrets (en Cloud)
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", None)
PROTECTORA_EMAIL = st.secrets.get("PROTECTORA_EMAIL", None)  # opcional

# -------------------------------
# Funciones
# -------------------------------
def clasificar_adoptante(
    edad, tiempo_libre, redes_seguridad, experiencia, tipo_vivienda, permiso_mascotas
):
    # 🚫 Descalificador: sin permiso de mascotas
    if permiso_mascotas == "No":
        return -1, "NO APTO", "error"

    puntos = 0

    # Edad (tramos)
    if edad < 25:
        puntos += 1
    elif 25 <= edad <= 44:
        puntos += 2
    elif 45 <= edad <= 60:
        puntos += 1
    else:  # > 60
        puntos -= 1

    # Tiempo disponible
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
    if tipo_vivienda in ["Piso", "Casa/Chalet", "Casa"]:
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

# =========================
# 1) FORMULARIO
# =========================
st.markdown("<div id='formulario'></div>", unsafe_allow_html=True)
st.header("Formulario de adopción")
st.title("🐾 AdoptAPP")
st.subheader("Cuestionario de preevaluación")
st.markdown("Completa el formulario. Revisaremos tu solicitud a la mayor brevedad.")

    with st.form("adoption_form"):
        # Datos básicos
        nombre = st.text_input("👤 Nombre completo del adoptante")
        telefono = st.text_input("📱 Teléfono de contacto (móvil)")
        nombre_animal = st.text_input("🐶😺 Nombre del animal que quieres adoptar")

        # Perfil
        edad = st.slider("Edad", 18, 80, 30)
        genero = st.selectbox("Género", ["Mujer", "Hombre", "No me representa"])
        ubicacion = st.text_input("Ciudad / Provincia")
        tipo_vivienda = st.selectbox("Tipo de vivienda", ["Piso", "Casa", "Ático", "Vivienda Compartida"])

        # Alquiler/permiso (una sola pregunta)
        permiso_mascotas = st.radio(
            "🏠 ¿Vives de alquiler y tienes permiso para tener mascotas?",
            ["Sí", "No", "No aplica (vivienda propia)"]
        )

        # Tiempo disponible 
        tiempo_libre = st.selectbox(
            "¿Cuánto tiempo tienes al día para el animal?",
            ["1-2 horas", "2-5 horas", ">5 horas"]
        )

        # Seguridad y experiencia
        redes_seguridad = st.radio(
            "¿Estás dispuesto/a a instalar redes de seguridad en ventanas/balcones para el gato?",
            ["Sí", "No", "No aplica"]
        )
        experiencia = st.selectbox(
            "¿Cuál es tu experiencia con animales de compañía?",
            ["Baja", "Media", "Alta"]
        )

        # Consentimiento de envío a protectora
        consent = st.checkbox(
            "Autorizo a enviar mi solicitud a la protectora para su evaluación",
            value=False
        )

        # Botón de envío
        submit = st.form_submit_button("Enviar solicitud")

    # Resultado y envío
    if submit:
        puntos, etiqueta, color = clasificar_adoptante(
            edad, tiempo_libre, redes_seguridad, experiencia, tipo_vivienda, permiso_mascotas
        )

        st.markdown("### 🧠 Evaluación del sistema:")
        if color == "success":
            st.success("✅ Alta probabilidad de ser un adoptante responsable. Se recomienda avanzar con la entrevista.")
        elif color == "warning":
            st.warning("⚠️ Perfil intermedio. Requiere evaluación manual adicional.")
        else:
            st.error("❌ Perfil con bajo encaje inicial. Se recomienda revisar motivaciones y condiciones.")

        # Payload (no se muestra al usuario)
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

        # Envío silencioso (solo confirmación/errores)
        if consent:
            ok, msg = enviar_resumen_por_webhook(resumen, WEBHOOK_URL)
            if ok:
                st.success("✅ Tu solicitud se ha enviado correctamente a la protectora.")
            else:
                st.error("⚠️ No se pudo enviar automáticamente. Por favor, inténtalo de nuevo más tarde.")
        else:
            st.info("ℹ️ No se enviará la solicitud porque no diste consentimiento.")

        st.markdown("---")
        st.markdown("📝 **Nota:** Esta evaluación es preliminar y no sustituye el criterio del personal de la protectora.")

    # RGPD (se muestra en la página del formulario)
    st.caption("Al enviar, confirmas que la información facilitada es veraz. El envío a la protectora solo se realizará si otorgas tu consentimiento.")
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

# =========================
# 2) ANIMALES
# =========================
st.markdown("<div id='animales'></div>", unsafe_allow_html=True)
st.header("Animales en adopción")
st.title("🐕 Animales en adopción")
st.info("Aquí podrías mostrar un listado con fotos y fichas de animales en adopción.")
st.image("https://place-puppy.com/300x300", caption="Luna - 2 años, Protectora A")
st.image("https://placekitten.com/300/300", caption="Michi - 1 año, Protectora B")

# =========================
# 3) TIPS
# =========================
st.markdown("<div id='tips'></div>", unsafe_allow_html=True)
st.header("Tips de alimentación")
st.title("🍖 Tips de alimentación y cuidados")
st.markdown("- [Guía sobre piensos](https://example.com)")
st.markdown("- [Tiendas recomendadas](https://example.com)")

# =========================
# 4) HISTORIAS
# =========================
st.markdown("<div id='historias'></div>", unsafe_allow_html=True)
st.header("Historias de adopción")
st.title("📖 Historias de adopciones exitosas")
st.success("“Luna fue adoptada en 2023 y ahora vive feliz con su nueva familia.”")
st.image("https://place-puppy.com/400x300")

# =========================
# 5) LEY
# =========================
st.markdown("<div id='ley'></div>", unsafe_allow_html=True)
st.header("Ley de Bienestar Animal")
st.markdown("Resumen de los puntos clave de la ley...")
st.markdown("[Consulta el texto completo en el BOE](https://www.boe.es)")

