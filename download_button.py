from io import BytesIO
import re
import streamlit as st
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import numpy as np
from PIL import ImageDraw

def latex_to_image(formula, fontSize=12, dpi=300, is_block=False):
    """Renderiza ecuaciones LaTeX como imágenes con mejor calidad y detección de variables."""
    try:
        if not formula or formula.strip() == "":
            raise ValueError("La fórmula está vacía. Verifica la entrada.")

        # Eliminar signos de dólar adicionales si existen
        formula = formula.strip().strip("$")
        
        # Comprobación adicional para variables sueltas (a, b, c, etc.)
        if len(formula) == 1 and formula.isalpha():
            formula = f"{formula}"  # Asegurar que se renderice como variable
            
        # Preprocesar la fórmula para asegurar que ciertos símbolos se interpreten correctamente
        # Por ejemplo, asegurar que los "^" tengan llaves si es necesario
        if "^" in formula and not "^{" in formula:
            formula = re.sub(r'\^(\d+)', r'^{\1}', formula)
        
        # Ajustar tamaño basado en el tipo de fórmula y su longitud
        if is_block:
            # Para fórmulas de bloque, dar más espacio horizontal
            length_factor = min(max(0.8, len(formula) / 20), 2.5)
            fig_width = 5 * length_factor
            fig_height = 1.0
            font_size_adjusted = fontSize   # Mayor tamaño para fórmulas de bloque
        else:
            # Para fórmulas inline, más compactas
            length_factor = min(max(0.8, len(formula) / 20), 2.5)
            fig_width = 5 * length_factor
            fig_height = 1.0
            font_size_adjusted = fontSize
        
        # Crear figura con fondo transparente
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
        ax = fig.add_subplot(111)
        ax.axis("off")
        
        # Configurar márgenes mínimos
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        
        # Utilizar formato LaTeX para renderizar
        ax.text(0.5, 0.5, r"$" + formula + r"$", 
                fontsize=font_size_adjusted, ha="center", va="center", 
                transform=ax.transAxes)
        
        # Guardar imagen con calidad alta
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", 
                   pad_inches=0.02, transparent=True)
        plt.close(fig)
        buf.seek(0)
        
        # Mejorar contraste y calidad
        img = Image.open(buf)
        
        # Recortar bordes blancos excesivos
        img_data = np.array(img)
        non_empty_columns = np.where(img_data.min(axis=0).min(axis=1) < 250)[0]
        non_empty_rows = np.where(img_data.min(axis=1).min(axis=1) < 250)[0]
        
        if len(non_empty_rows) > 0 and len(non_empty_columns) > 0:
            cropBox = (min(non_empty_columns), min(non_empty_rows),
                       max(non_empty_columns), max(non_empty_rows))
            img_cropped = img.crop(cropBox)
            
            # Añadir un pequeño padding
            new_size = (img_cropped.width + 20, img_cropped.height + 10) 
            new_img = Image.new("RGBA", new_size, (255, 255, 255, 0))
            new_img.paste(img_cropped, (10, 5))
            return new_img
        
        return img

    except Exception as e:
        print(f"Error al renderizar LaTeX: {e}")
        
        # Crear una imagen de texto plano como fallback
        img = Image.new('RGB', (300, 50), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), f"[Error en fórmula: {formula}]", fill=(0, 0, 0))
        return img

def procesar_contenido_mejorado(content):
    """Divide el contenido con mejor detección de expresiones LaTeX."""
    # Patrón más robusto para detectar fórmulas LaTeX
    pattern = r'(\$\$.*?\$\$|\$.*?\$|\\begin\{.*?\}.*?\\end\{.*?\})'
    
    # Dividir primero por fórmulas de bloque para tratarlas separadamente
    block_pattern = r'(\$\$.*?\$\$|\\begin\{.*?\}.*?\\end\{.*?\})'
    parts = re.split(block_pattern, content, flags=re.DOTALL)
    
    elementos = []
    for part in parts:
        if part.startswith("$$") and part.endswith("$$") or \
           part.startswith("\\begin{") and "\\end{" in part:
            # Fórmula de bloque
            elementos.append({"tipo": "formula_bloque", "contenido": part.strip("$")})
        else:
            # Buscar fórmulas inline en esta sección
            inline_parts = re.split(r'(\$.*?\$)', part)
            for inline_part in inline_parts:
                if inline_part.startswith("$") and inline_part.endswith("$"):
                    # Fórmula inline
                    elementos.append({"tipo": "formula_inline", "contenido": inline_part.strip("$")})
                elif inline_part.strip():
                    # Texto normal (no vacío)
                    elementos.append({"tipo": "texto", "contenido": inline_part})
    
    return elementos

def generar_pdf(messages):
    """Genera un PDF con los mensajes, con mejor integración de LaTeX."""
    
    
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    margin_x, margin_y = 50, 50
    y_position = height - margin_y
    text_width = width - 2 * margin_x


    current_page = c.getPageNumber()
    c.setFont("Helvetica", 8)
    c.drawString(width - margin_x - 40, margin_y - 20, f"Página {current_page}")


    def nueva_pagina():
        nonlocal y_position
        c.showPage()
        y_position = height - margin_y
        
        # Agregar encabezado en la nueva página
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin_x, height - 25, "Clases particulares La Pampa")
        c.line(margin_x, height - 30, width - margin_x, height - 30)

        current_page = c.getPageNumber()
        c.setFont("Helvetica", 8)
        c.drawString(width - margin_x - 40, margin_y - 20, f"Página {current_page}")

    
    # Logo y título - mantenemos igual que antes ya que te gustó
    logo_path = "logs/front-log.png"
    try:
        logo = ImageReader(logo_path)
        c.drawImage(logo, margin_x, height - 90, width=50, height=50, mask="auto")
    except Exception as e:
        print(f"Error al cargar el logo: {e}")
    
    # Título centrado y con mejor formato
    titulo = "Clases particulares La Pampa"
    c.setFont("Helvetica-Bold", 20)
    titulo_ancho = c.stringWidth(titulo, "Helvetica-Bold", 20)
    c.drawString((width - titulo_ancho) / 2, height - 60, titulo)
    c.setLineWidth(1)
    c.line((width - titulo_ancho * 1.1) / 2, height - 65, (width + titulo_ancho * 1.1) / 2, height - 65)
    y_position -= 90
    

    # Procesar mensajes
    for message in messages:
        # Verificar si hay suficiente espacio para el nuevo mensaje
        if y_position < margin_y + 150:
            nueva_pagina()
        
        role = "Usuario" if message["role"] == "user" else "Profesor"
        color_texto = colors.HexColor("#3498db") if role == "Usuario" else colors.HexColor("#2c3e50")
        fondo_mensaje = colors.HexColor("#ecf0f1") if role == "Usuario" else colors.HexColor("#d5dbdb")
        
        # Encabezado del mensaje
        c.setFillColor(fondo_mensaje)
        alto_encabezado = 22
        c.rect(margin_x - 5, y_position, text_width + 10, alto_encabezado, fill=1, stroke=0)
        
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(color_texto)
        c.drawString(margin_x, y_position + 6, f"{role}:")
        y_position -= 30
        
        # Procesar el contenido con manejo mejorado de LaTeX
        elementos = procesar_contenido_mejorado(message["content"])
        
        formula_anterior = False  # Controlar si acabamos de mostrar una fórmula
        
        for i, elemento in enumerate(elementos):
            # Verificar espacio disponible
            if y_position < margin_y + 50:
                nueva_pagina()
                
            if elemento["tipo"] == "texto":
                texto = elemento["contenido"].strip()
                if texto:
                    # Manejar mejor el espacio después de fórmulas
                    if formula_anterior and not texto.startswith(('.', ',', ':', ';', '?', '!')):
                        y_position += 8  # Reducir espacio extra si el texto continúa una oración
                    
                    c.setFont("Helvetica", 10)
                    c.setFillColor(colors.black)
                    
                    # Dividir por líneas para mejor control
                    lineas = texto.split('\n')
                    for linea in lineas:
                        # Procesar línea por línea
                        words = linea.split()
                        line = ""
                        
                        for word in words:
                            word_width = c.stringWidth(word + " ", "Helvetica", 10)
                            next_width = c.stringWidth(line + word + " ", "Helvetica", 10)
                            
                            if next_width > text_width:
                                c.drawString(margin_x, y_position, line.strip())
                                y_position -= 16
                                line = word + " "
                            else:
                                line += word + " "
                        
                        # Dibujar línea final
                        if line.strip():
                            c.drawString(margin_x, y_position, line.strip())
                            y_position -= 16
                            
                    formula_anterior = False
                    
            elif elemento["tipo"] in ["formula_bloque", "formula_inline"]:
                is_block = elemento["tipo"] == "formula_bloque"
                formula = elemento["contenido"].strip()
                
                if formula:
                    # Generar imagen de la fórmula con calidad mejorada
                    image = latex_to_image(formula, 
                                          fontSize=14 if is_block else 14,
                                          dpi=300,
                                          is_block=is_block)
                    
                    if image:
                        buf = BytesIO()
                        image.save(buf, format="PNG")
                        buf.seek(0)
                        
                        img_width, img_height = image.size
                        
                        # Ajustar tamaño según tipo de fórmula
                        if is_block:
                            # Fórmulas de bloque centradas
                            max_width = text_width * 0.9
                            scale_factor = min(1.0, max_width / img_width)
                            actual_width = img_width * scale_factor
                            actual_height = img_height * scale_factor
                            x_position = margin_x + (text_width - actual_width) / 2
                            
                            # Espacio adicional antes de bloques
                            y_position -= 8
                        else:
                            # Fórmulas inline integradas en el texto
                            max_width = text_width * 0.7
                            scale_factor = min(1.0, max_width / img_width)
                            actual_width = img_width * scale_factor
                            actual_height = img_height * scale_factor
                            x_position = margin_x + 5
                            
                            # Para variables sueltas, usar menos espacio
                            if len(formula.strip()) <= 2:
                                actual_height *= 0.8
                        
                        # Verificar espacio disponible
                        if y_position - actual_height < margin_y:
                            nueva_pagina()
                        
                        # Dibujar la imagen
                        c.drawImage(ImageReader(buf), x_position, y_position - actual_height,
                                   width=actual_width, height=actual_height, mask="auto")
                        
                        # Ajustar posición según tipo
                        if is_block:
                            y_position -= (actual_height + 15)
                        else:
                            y_position -= (actual_height + 5)
                            
                        formula_anterior = True
                        
                        # Verificar el siguiente elemento para ajustar espacio
                        if i < len(elementos) - 1 and elementos[i+1]["tipo"] == "texto":
                            siguiente_texto = elementos[i+1]["contenido"].strip()
                            if siguiente_texto and siguiente_texto[0] in ('.', ',', ':', ';', '?', '!'):
                                y_position += 8  # Reducir espacio si sigue un signo de puntuación
        
        # Espacio entre mensajes
        y_position -= 15
        
        # Línea divisoria entre mensajes
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(margin_x, y_position + 5, margin_x + text_width, y_position + 5)
        
        # Nueva página si es necesario
        if y_position < margin_y + 50:
            nueva_pagina()
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def renderizar_boton_descarga():
    """Renderiza un botón para descargar la conversación como PDF en Streamlit."""
    if "messages" not in st.session_state or not st.session_state.messages:
        st.sidebar.warning("No hay mensajes para descargar.")
        return

    messages_copy = list(st.session_state.messages)

    pdf_buffer = generar_pdf(messages_copy)  # Generar el PDF con la conversación más reciente

    st.sidebar.download_button(
        label="Descargar conversación",
        data=pdf_buffer,
        file_name="chat_con_profesor.pdf",
        mime="application/pdf"
    )
