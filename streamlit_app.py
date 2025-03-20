import streamlit as st
import google.generativeai as genai
from PIL import Image
import frontend
import uuid
import download_button

# Configuración inicial
st.set_page_config(
    page_title="Asistente de Matemáticas",
    layout="centered",
    page_icon="logs/front-log.webp"
)

# Inicializar estado si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False

# Cachear imágenes y textos
@st.cache_data
def load_image(path):
    return Image.open(path)

@st.cache_data
def cargar_texto(path):
    with open(path, "r", encoding="utf-8") as archivo:
        return archivo.read()

# Cargar instrucciones y contenido base
MATH_INSTRUCTIONS = cargar_texto("math_instructions.md")
PRELIMINARES_MATEMATICA = cargar_texto("preliminares_matematica.md")

# Cargar avatares
front_logo = load_image("logs/front-log.png")
user_logo = load_image("logs/user_avatar.png")

# Aplicar estilos personalizados
frontend.render_custom_styles()
frontend.render_title()

# Si el chat no ha sido activado, mostrar el botón de inicio
if not st.session_state.chat_active:
    frontend.render_intro()
    
    if st.button("### Comenzar", key="start_button"):
        st.session_state.chat_active = True
        st.rerun()

# Función para renderizar mensajes con soporte para LaTeX
def render_mensaje_con_latex(texto):
    import re
    bloques = re.split(r"(\$\$.*?\$\$)", texto)  # Divide por ecuaciones en bloque
    for bloque in bloques:
        if bloque.startswith("$$") and bloque.endswith("$$"):
            st.latex(bloque.strip("$$"))  # Renderiza ecuaciones en bloque
        else:
            bloque = re.sub(r"(\$.*?\$)", r" \1 ", bloque)  # Espacios en ecuaciones inline
            st.write(bloque)  # Renderiza texto con ecuaciones inline

# Si el chat está activado, mostrar mensajes y permitir interacción
if st.session_state.chat_active:
    st.markdown("<b>¡Bienvenido! Escribe tu primera pregunta</b>", unsafe_allow_html=True)

    # Mostrar botón de descarga si hay mensajes previos
    def descargar_conversacion():   
        download_button.renderizar_boton_descarga()   
        
    if len(st.session_state.messages) > 0:
        with st.sidebar:
            st.markdown("### Guardar conversación")
            st.button("Preparar descarga", on_click=descargar_conversacion)
                

    # Renderizar mensajes en orden (primero los antiguos, luego los nuevos)
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="logs/front-log.png"):
                render_mensaje_con_latex(message["content"])
        else:
            with st.chat_message("user", avatar="logs/user_avatar.png"):
                st.markdown(message["content"], unsafe_allow_html=True)

    # Input para enviar mensajes
    prompt = st.chat_input("Escribe tu mensaje aquí...")

    if prompt:
        # Guardar el mensaje del usuario en la sesión y mostrarlo
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)

        # Renderizar el mensaje del usuario
        with st.chat_message("user", avatar="logs/user_avatar.png"):
            st.markdown(prompt, unsafe_allow_html=True)

        # Crear contexto inicial con instrucciones y contenido del libro
        initial_context = [
            {"role": "system", "content": "Es OBLIGATORIO que EVITES utilizar texto plano para las operaciones matemáticas, hasta en las operaciones matemáticas que escribas en texto plano y SIEMPRE debas usar formato LaTeX. Por ejemplo, $x^2 + 2x + 1 = 0$. Devuelve las ecuaciones matemáticas según las reglas establecidas."},
            {"role": "system", "content": MATH_INSTRUCTIONS},
            {"role": "assistant", "content": PRELIMINARES_MATEMATICA},
        ]

        # Configurar API de Gemini
        genai.configure(api_key=st.secrets["google"]["api_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Obtener respuesta del asistente
        response = model.generate_content(
            [m["content"] for m in (initial_context + st.session_state.messages)],
            generation_config={
                "temperature": 0.3,
                "top_p": 0.1,
                "max_output_tokens": 2048,
            }
        )

        response_content = response.text  # Obtener la respuesta en texto

        # Guardar la respuesta del asistente en la sesión
        assistant_message = {"role": "assistant", "content": response_content}
        st.session_state.messages.append(assistant_message)

        # Renderizar correctamente el mensaje del asistente con LaTeX
        with st.chat_message("assistant", avatar="logs/front-log.png"):
            render_mensaje_con_latex(response_content)
