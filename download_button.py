from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, blue, grey
from reportlab.lib.utils import simpleSplit
import os
import re
import streamlit as st

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.textlabels import Label

def latex_to_image(c, formula, x, y, fontSize=14, center=False):
    """Renderiza ecuaciones LaTeX como imágenes."""
    drawing = Drawing(0, 0)
    math_text = Label()
    math_text.setText(formula)
    math_text.fontSize = fontSize

    try:
        bounds = math_text.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
    except:
        width, height = 100, 30

    drawing.add(math_text)

    if center:
        x = x - (width / 2)

    c.saveState()
    c.translate(x, y - height + 5)
    c.scale(min(100, width) / width, min(20, height) / height)
    drawing.drawOn(c, 0, 0)
    c.restoreState()

    return height + 10  

def generar_pdf(messages):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    margin_x = 40
    margin_y = 50
    max_width = width - 2 * margin_x  
    line_height = 16  
    y_position = height - 100  
    primera_pagina = True  

    def nueva_pagina():
        nonlocal y_position, primera_pagina
        c.showPage()
        y_position = height - 50  
        primera_pagina = False  

    # Agregar logo (solo en la primera página)
    logo_path = "logs/front-log.png"
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, margin_x, height - 100, width=100, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            st.warning(f"⚠️ Error cargando la imagen: {e}")

    # Dibujar título (solo en la primera página)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Chat descargado con Profesor")
    c.line(margin_x, height - 60, width - margin_x, height - 60)

    for message in messages:
        role = "Usuario" if message["role"] == "user" else "Profesor"

        c.setFillColor(blue if message["role"] == "user" else black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y_position, f"{role}:")
        y_position -= line_height

        c.setFillColor(black)
        c.setFont("Helvetica", 12)

        content_parts = re.split(r"(\$\$.*?\$\$)", message["content"])  # Separar ecuaciones en bloque
        for part in content_parts:
            if part.startswith("$$") and part.endswith("$$"):
                formula = part[2:-2].strip()
                img_height = latex_to_image(c, formula, width / 2, y_position, fontSize=16, center=True)
                y_position -= img_height  
                if y_position < margin_y:
                    nueva_pagina()
            else:
                text_parts = re.split(r"(\$.*?\$)", part)  # Separar ecuaciones en línea
                for text in text_parts:
                    if text.startswith("$") and text.endswith("$"):
                        formula = text[1:-1].strip()
                        img_height = latex_to_image(c, formula, margin_x + 10, y_position, fontSize=12, center=False)
                        y_position -= img_height
                        if y_position < margin_y:
                            nueva_pagina()
                    else:
                        lines = text.split("\n")
                        for line in lines:
                            line = line.strip()
                            if line.startswith("###"):  # Títulos
                                title_text = line.replace("###", "").strip()
                                y_position -= 10  
                                c.setFont("Helvetica-Bold", 14)
                                c.drawString(margin_x, y_position, title_text)
                                y_position -= line_height + 5  
                                c.setFont("Helvetica", 12)  
                            elif "**" in line:  # Subtítulos en gris
                                subtitle_text = line.replace("**", "").strip()
                                y_position -= 5  
                                c.setFillColor(grey)
                                c.setFont("Helvetica-Oblique", 12)  
                                c.drawString(margin_x + 5, y_position, subtitle_text)
                                y_position -= line_height  
                                c.setFont("Helvetica", 12)  
                                c.setFillColor(black)  
                            else:  # Texto normal
                                content_lines = simpleSplit(line, "Helvetica", 12, max_width)
                                for subline in content_lines:
                                    c.drawString(margin_x + 10, y_position, subline)  
                                    y_position -= line_height
                                    if y_position < margin_y:
                                        nueva_pagina()

        y_position -= line_height * 1.5  

        if y_position < margin_y:
            nueva_pagina()

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def renderizar_boton_descarga(messages):
    pdf_buffer = generar_pdf(messages)
    st.sidebar.download_button(
        label="Descargar conversación",
        data=pdf_buffer,
        file_name="chat_con_profesor.pdf",
        mime="application/pdf"
    )
