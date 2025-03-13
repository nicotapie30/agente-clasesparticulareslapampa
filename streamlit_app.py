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
        st.rerun()  # Corrección: Usar st.rerun() en lugar de st.experimental_rerun()

# Función para renderizar respuestas con LaTeX correctamente
def render_mensaje_con_latex(texto):
    """
    Renderiza un mensaje en Streamlit, mostrando las ecuaciones en LaTeX correctamente.
    - Ecuaciones en bloque `$$ ... $$` se muestran con `st.latex()`
    - Texto y ecuaciones inline `$ ... $` se procesan con `st.markdown()`
    """
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

    st.markdown(f"""<b>¡Bienvenido! Escribe tu primera pregunta</B>""",
        unsafe_allow_html=True)

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
            if message["role"] == "assistant":
                render_mensaje_con_latex(message["content"])  # Renderiza correctamente el LaTeX
            else:
                frontend.render_chat_message("user", message["content"], avatar=avatar)
            st.session_state.rendered_message_ids.add(message_id)

    # Input para enviar mensajes (solo aparece después de hacer clic en "Comenzar")
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        # Guardar el mensaje del usuario en la sesión y mostrarlo
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        frontend.render_chat_message("user", prompt, avatar=user_logo)

        # Crear contexto inicial con instrucciones y contenido del libro
        contexto_inicial = [
            {"role": "system", "content": "Es OBLIGATORIO que EVITES utilizar texto plano para las operaciones matemáticas, hasta en las operaciones matemáticas que escribas en texto plano y SIEMPRE debas usar formato LaTeX. Por ejemplo, $x^2 + 2x + 1 = 0$. Devuelve las ecuaciones matemáticas según las reglas establecidas."},
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
        response_content = response.choices[0].message.content

        # Guardar y mostrar la respuesta del asistente
        assistant_message = {"role": "assistant", "content": response_content}
        st.session_state.messages.append(assistant_message)

        # Renderizar correctamente el mensaje del asistente con LaTeX
        render_mensaje_con_latex(response_content)
