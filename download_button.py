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
        fig, ax = plt.subplots(figsize=(0.01, 0.01))
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
    text_width = width - 2 * margin_x 

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

        # Definir colores según el rol
        color = colors.HexColor("#3498db") if role == "Usuario" else colors.black  # Azul para usuario, negro para profesor

        # Encabezado del mensaje
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(color)  # Aplica color al texto
        c.drawString(margin_x, y_position, f"{role}:")
        y_position -= 15

        # Procesar el contenido
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)  # El contenido siempre en negro para legibilidad
        words = message["content"].split()
        buffer = ""

        content_parts = re.split(r"(\$\$.*?\$\$|\$.*?\$)", message["content"])
        for part in content_parts:
            if part.startswith("$$") and part.endswith("$$"):
                formula = part.strip("$$").strip()
                image = latex_to_image(formula, fontSize=16)
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
                    y_position -= img_height + 10
                    if y_position < margin_y:
                        nueva_pagina()
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

def renderizar_boton_descarga(messages):
    """Renderiza un botón para descargar la conversación como PDF en Streamlit."""
    pdf_buffer = generar_pdf(messages)
    st.sidebar.download_button(
        label="Descargar conversación",
        data=pdf_buffer,
        file_name="chat_con_profesor.pdf",
        mime="application/pdf"
    )
