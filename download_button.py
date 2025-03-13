import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, blue, grey
from reportlab.lib.utils import simpleSplit
import os
import streamlit as st
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.textlabels import Label

def latex_to_image(c, formula, x, y, fontSize=14, center=False, max_width=180):
    """Renderiza ecuaciones LaTeX como imágenes sin salirse del margen."""
    drawing = Drawing(0, 0)
    math_text = Label()
    math_text.setText(formula)
    math_text.fontSize = fontSize

    try:
        bounds = math_text.getBounds()
        width = max(1, bounds[2] - bounds[0])  
        height = max(1, bounds[3] - bounds[1])  
    except:
        width, height = 100, 30  

    drawing.add(math_text)

    if center:
        x = max(40, x - (width / 2))  

    scale_factor = min(max_width / width, 1)  

    c.saveState()
    c.translate(x, y - height + 5)
    c.scale(scale_factor, scale_factor)  
    drawing.drawOn(c, 0, 0)
    c.restoreState()

    return height * scale_factor + 10  

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

        content_parts = re.split(r"(\$\$.*?\$\$)", message["content"])  
        for part in content_parts:
            if part.startswith("$$") and part.endswith("$$"):
                formula = part[2:-2].strip()
                y_position -= 10  # Espacio antes de ecuaciones en bloque
                img_height = latex_to_image(c, formula, width / 2, y_position, fontSize=16, center=True)
                y_position -= img_height + 10  # Espacio después de la ecuación  
                if y_position < margin_y:
                    nueva_pagina()
            else:
                text_parts = re.split(r"(\$.*?\$)", part)  
                line_buffer = []
                for text in text_parts:
                    if text.startswith("$") and text.endswith("$"):
                        formula = text[1:-1].strip()
                        if line_buffer:
                            c.drawString(margin_x + 10, y_position, " ".join(line_buffer))
                            y_position -= line_height
                            line_buffer = []
                        img_height = latex_to_image(c, formula, margin_x + 10, y_position, fontSize=12, center=False)
                        y_position -= img_height
                        if y_position < margin_y:
                            nueva_pagina()
                    else:
                        lines = text.split("\n")
                        for line in lines:
                            line = line.strip()
                            if line.startswith("###"):  # Títulos
                                if line_buffer:
                                    c.drawString(margin_x + 10, y_position, " ".join(line_buffer))
                                    y_position -= line_height
                                    line_buffer = []
                                title_text = line.replace("###", "").strip()
                                y_position -= 10  
                                c.setFont("Helvetica-Bold", 14)
                                c.drawString(margin_x, y_position, title_text)
                                y_position -= line_height + 5  
                                c.setFont("Helvetica", 12)  
                            elif "**" in line:  # Subtítulos en gris
                                if line_buffer:
                                    c.drawString(margin_x + 10, y_position, " ".join(line_buffer))
                                    y_position -= line_height
                                    line_buffer = []
                                subtitle_text = line.replace("**", "").strip()
                                y_position -= 5  
                                c.setFillColor(grey)
                                c.setFont("Helvetica-Oblique", 12)  
                                c.drawString(margin_x + 5, y_position, subtitle_text)
                                y_position -= line_height  
                                c.setFont("Helvetica", 12)  
                                c.setFillColor(black)  
                            else:
                                line_buffer.append(line)
                if line_buffer:
                    c.drawString(margin_x + 10, y_position, " ".join(line_buffer))
                    y_position -= line_height

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
