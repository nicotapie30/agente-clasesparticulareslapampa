from io import BytesIO
import re
import streamlit as st
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
from reportlab.lib import colors

def latex_to_image(formula, fontSize=14, dpi=300):
    """Renderiza ecuaciones LaTeX como imágenes usando Matplotlib."""
    try:
        if not formula or formula.strip() == "":
            raise ValueError("La fórmula está vacía. Verifica la entrada.")

        # Eliminar signos de dólar adicionales si existen
        formula = formula.strip().strip("$")

        # Eliminar \displaystyle (si está presente)
        formula = formula.replace(r"\displaystyle", "")

        # Envolver la fórmula en delimitadores de LaTeX
        formula = r"$" + formula + r"$"

        # Configuración del gráfico
        fig, ax = plt.subplots(figsize=(0.5, 0.3))
        ax.axis("off")
        ax.text(0.5, 0.5, formula, fontsize=fontSize, ha="center", va="center")

        # Guardar la imagen en memoria
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1, transparent=True)
        plt.close(fig)
        buf.seek(0)

        return Image.open(buf)

    except Exception:
        return None 
    


def generar_pdf(messages):
    """Genera un PDF con los mensajes, aplicando colores diferenciados."""
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    margin_x, margin_y = 40, 50
    y_position = height - margin_y
    text_width = width - 2 * margin_x - 20

    def nueva_pagina():
        nonlocal y_position
        c.showPage()
        y_position = height - margin_y

    titulo = "Chat con Profesor"
    c.setFont("Helvetica-Bold", 18)  # 🔹 Aumentar tamaño de letra
    titulo_ancho = c.stringWidth(titulo, "Helvetica-Bold", 18)
    c.drawString((width - titulo_ancho) / 2, height - 60, titulo)  # 🔹 Centrar título
    c.line((width - titulo_ancho) / 2, height - 65, (width + titulo_ancho) / 2, height - 65) 
    y_position -= 80

    for message in messages:
        role = "Usuario" if message["role"] == "user" else "Profesor"
        color_texto = colors.HexColor("#3498db") if role == "Usuario" else colors.HexColor("#2c3e50")
        fondo_mensaje = colors.HexColor("#ecf0f1") if role == "Usuario" else colors.HexColor("#d5dbdb")

        # 🔹 Dibujar fondo para el mensaje
        c.setFillColor(fondo_mensaje)
        alto_mensaje = 20  # Reducir espacio
        y_position -= alto_mensaje
        c.rect(margin_x - 5, y_position, text_width + 10, alto_mensaje, fill=1, stroke=0)
        
        # 🔹 Encabezado (Usuario / Profesor)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(color_texto)
        c.drawString(margin_x, y_position + 8, f"{role}:")
        y_position -= 18

        # 🔹 Procesar el contenido (incluyendo LaTeX en el flujo del texto)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        content_parts = re.split(r"(\$.*?\$)", message["content"])  
        buffer = ""

        content_parts = re.split(r"(\$\$.*?\$\$|\$.*?\$)", message["content"])

        for part in content_parts:
            if part.startswith("$$") and part.endswith("$$"):
                formula = part.strip("$$").strip()
                image = latex_to_image(formula, fontSize=12)
                if image:
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    buf.seek(0)
                    img_width, img_height = image.size
                    scale_factor = 0.25
                    img_width *= scale_factor
                    img_height *= scale_factor
                    x_position = (width - img_width) / 2
                    c.drawImage(ImageReader(buf), x_position, y_position - img_height, width=img_width, height=img_height, mask="auto")
                    y_position -= img_height + 10
                    if y_position < margin_y:
                        nueva_pagina()
                    c.setFont("Helvetica", 9)
            elif part.startswith("$") and part.endswith("$"):
                formula = part.strip("$").strip()
                image = latex_to_image(formula, fontSize=12)
                if image:
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    buf.seek(0)
                    img_width, img_height = image.size
                    scale_factor = 0.3
                    img_width *= scale_factor
                    img_height *= scale_factor
                    x_position = (width - img_width) / 2
                    c.drawImage(ImageReader(buf), x_position, y_position - img_height, width=img_width, height=img_height, mask="auto")
                    y_position -= img_height + 5
                    if y_position < margin_y:
                        nueva_pagina()
            else:
                words = part.split()
                buffer = ""
                for word in words:
                    if c.stringWidth(buffer + word + " ", "Helvetica", 10) < text_width:
                        buffer += word + " "
                    else:
                        c.drawString(margin_x, y_position, buffer.strip())
                        y_position -= 15
                        if y_position < margin_y:
                            nueva_pagina()
                        buffer = word + " "
                if buffer.strip():
                    c.drawString(margin_x, y_position, buffer.strip())
                    y_position -= 15
                    if y_position < margin_y:
                        nueva_pagina()

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def renderizar_boton_descarga():
    """Renderiza un botón para descargar la conversación como PDF en Streamlit."""
    if "messages" not in st.session_state or not st.session_state.messages:
        st.sidebar.warning("No hay mensajes para descargar.")
        return

    # 💡 Tomar la última versión de la conversación
    messages_copy = list(st.session_state.messages)

    pdf_buffer = generar_pdf(messages_copy)  # Generar el PDF con la conversación más reciente

    st.sidebar.download_button(
        label="Descargar conversación",
        data=pdf_buffer,
        file_name="chat_con_profesor.pdf",
        mime="application/pdf"
    )
