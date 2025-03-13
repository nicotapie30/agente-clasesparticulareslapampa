import streamlit as st
from openai import OpenAI
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

# Inicializar estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rendered_message_ids" not in st.session_state:
    st.session_state.rendered_message_ids = set()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False  # Control del estado del chat

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
front_logo = load_image("logs/front-log.webp")
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

# Si el chat está activado, mostrar mensajes y permitir interacción
if st.session_state.chat_active:
    st.markdown("<b>¡Bienvenido! Escribe tu primera pregunta</b>", unsafe_allow_html=True)

    # Mostrar botón de descarga si hay mensajes previos
    if st.session_state.messages:
        with st.sidebar:
            st.markdown("### Guardar conversación")
            download_button.renderizar_boton_descarga(st.session_state.messages)

    # Renderizar mensajes anteriores y nuevos
    for i, message in enumerate(st.session_state.messages):
        message_id = f"{message['role']}-{i}"
        if message_id not in st.session_state.rendered_message_ids:
            avatar = front_logo if message["role"] == "assistant" else user_logo
            frontend.render_chat_message(message["role"], message["content"], avatar=avatar)
            st.session_state.rendered_message_ids.add(message_id)

    def limpiar_latex(respuesta):
        """Elimina caracteres invisibles y espacios innecesarios en LaTeX."""
        return respuesta.replace("\xa0", " ").strip()

    def validar_respuesta_matematica(respuesta):
        """Valida que las respuestas matemáticas estén bien formateadas."""
        if "$" not in respuesta and "$$" not in respuesta:
            return respuesta  # Respuesta no matemática permitida
        return limpiar_latex(respuesta)

    # Input para enviar mensajes
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        frontend.render_chat_message("user", prompt, avatar=user_logo)

        # Crear contexto inicial con instrucciones y contenido del libro
        contexto_inicial = [
            {"role": "system", "content": """
            Es OBLIGATORIO que TODAS las expresiones matemáticas estén en LaTeX.
            Nunca uses texto plano para ecuaciones o símbolos matemáticos.
            Usa SIEMPRE $ ... $ para expresiones en línea y $$ ... $$ para ecuaciones en bloque.
            Antes de enviar una respuesta, verifica que:
            1. Cada símbolo matemático esté en LaTeX.
            2. Cada ecuación esté dentro de $ ... $ (inline) o $$ ... $$ (bloque).
            3. No haya texto plano en expresiones matemáticas.
            Si encuentras errores en la respuesta generada, corrige automáticamente antes de enviarla.
            """},
            {"role": "system", "content": MATH_INSTRUCTIONS},
            {"role": "assistant", "content": PRELIMINARES_MATEMATICA},
        ]

        # Combinar contexto inicial con los mensajes previos
        mensajes_completos = contexto_inicial + st.session_state.messages

        # Obtener respuesta del asistente
        client = OpenAI(api_key=st.secrets["openai"]["api_key"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensajes_completos,
            temperature=0.3,
            top_p=0.1,
            frequency_penalty=0.2,
            presence_penalty=0.2,
        )
        response_content = validar_respuesta_matematica(response.choices[0].message.content)

        # Guardar y mostrar la respuesta del asistente
        assistant_message = {"role": "assistant", "content": response_content}
        st.session_state.messages.append(assistant_message)

        # Separar respuestas Markdown y LaTeX
        if "$" in response_content or "$$" in response_content:
            st.latex(response_content)  # Renderiza correctamente las expresiones matemáticas
        else:
            frontend.render_chat_message("assistant", response_content, avatar=front_logo)
