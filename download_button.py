from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, blue
from reportlab.lib.utils import simpleSplit
import os
import streamlit as st

def generar_pdf(messages):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    margin_x = 40
    margin_y = 50  # Margen inferior
    max_width = width - 2 * margin_x  # Ancho máximo para el texto
    line_height = 16  # Altura de línea ajustada
    y_position = height - 100  # Posición inicial del texto
    primera_pagina = True  # Flag para saber si estamos en la primera página

    def nueva_pagina():
        nonlocal y_position, primera_pagina
        c.showPage()
        y_position = height - 50  # Reiniciar la posición del texto en la nueva página
        primera_pagina = False  # Ya no estamos en la primera página

    # Agregar logo si existe (solo en la primera página)
    logo_path = "logs/front-log.png"
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, margin_x, height - 100, width=100, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            st.warning(f"⚠️ Error cargando la imagen: {e}")

    # Dibujar título y línea separadora (solo en la primera página)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Chat descargado con Profesor")
    c.line(margin_x, height - 60, width - margin_x, height - 60)

    for message in messages:
        role = "Usuario" if message["role"] == "user" else "Profesor"

        # Ajustar colores y negrita para los nombres
        c.setFillColor(blue if message["role"] == "assistant" else black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y_position, f"{role}:")
        y_position -= line_height

        # Volver al color negro para el contenido
        c.setFillColor(black)
        c.setFont("Helvetica", 12)

        # Dividir en líneas automáticas para que el texto no se salga
        content_lines = simpleSplit(message["content"], "Helvetica", 12, max_width)
        for line in content_lines:
            c.drawString(margin_x + 10, y_position, line)  # Texto con margen adicional
            y_position -= line_height

            # Si llegamos al margen inferior, pasamos a una nueva página
            if y_position < margin_y:
                nueva_pagina()

        y_position -= line_height  # Espacio entre mensajes

        # Si después de un mensaje estamos cerca del margen inferior, pasamos de página
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
