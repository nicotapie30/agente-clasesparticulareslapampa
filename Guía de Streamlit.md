# Guía para Manejo de la Aplicación en Streamlit

## 1. Acceso a la Aplicación

La aplicación es _privada_, por lo que solo los _usuarios autorizados_ pueden acceder. Para agregar usuarios, siga estos pasos:

### 1.1 Agregar Usuarios con Emails

1. Inicie sesión en la plataforma de [Streamlit Cloud](https://share.streamlit.io/). Si ya está autenticado, acceda directamente.
2. Vaya a la _configuración_ de su aplicación (haga clic en los tres puntos en la parte derecha de la página).
3. Busque la opción **Settings** o **Configuración**.
4. Dentro de **Settings**, vaya a la sección **Sharing** y agregue los _correos electrónicos_ de los usuarios autorizados, separados por comas (,).
5. Guarde los cambios (**Save changes**).

- Los usuarios recibirán un correo con instrucciones para acceder.

## 2. Configuración de API Key

Si la aplicación requiere una API Key para conectarse a servicios externos, siga estos pasos:

### 2.1 Agregar una API Key

1. Obtenga la API Key del servicio correspondiente.
2. En el código del proyecto de Streamlit, cree un archivo **secrets.toml** dentro de la carpeta **.streamlit** si aún no existe. _(Este archivo ya estaá creado)._ -> Salte al paso _4_
3. Agregue la clave en el archivo con el siguiente formato:
   ```toml
   [secrets]
   api_key = "TU_API_KEY_AQUI"
   ```
4. Alternativamente, en **Streamlit**, vaya a la _configuración_ de su aplicación, busque la opción **Settings** o **Configuración** y agregue la _API Key_ en la sección **Secrets**.

Para una API de Google Gemini, el formato específico sería:

```toml
[google]
api_key = "TU_API_KEY_AQUI"
```

## 3. Despliegue y Actualización de la Aplicación

Para actualizar la aplicación con cambios recientes:

1. Suba los cambios al repositorio de GitHub vinculado.
2. En **Streamlit**, vaya a la aplicación y seleccione **Rerun**, o espere a que se actualice automáticamente.

### 3.1 Comandos de Git para Subir Cambios _(Opcional)_

Si la aplicación está alojada en GitHub y desea subir cambios manualmente, siga estos pasos:

```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main  # O el nombre de la rama correspondiente
```

Si es la primera vez que sube los cambios, use:

```bash
git branch -M main
git remote add origin https://github.com/usuario/repositorio.git
git push -u origin main
```

## 4. Modificación de Instrucciones del Chatbot

### 4.2 Edición Directa desde GitHub

Puede editar los archivos directamente en el repositorio de GitHub para modificar su contenido:

- **preliminares_matematicas.md**: Proporciona el material base extraído del PDF de referencia para las respuestas.
- **math_instructions.md**: Define las _directivas_ y _prompts_ específicos que sigue el chatbot para responder.

### 4.3 Modificar archivo **preliminares_matematicas.md**:

1.  Debe dirigirse al archivo con ese nombre.
2.  Una vez dentro, puede dirigirse a cualquier bloque del archivo y modificar su contenido, o, si se quiere, modificar el archivo entero con un nuevo contenido.
3.  La manera de modificar todo el contenido, es extrayendo el texto del pdf, .docx, archivo.txt, etc y pegarlo a este archivo del proyecto, formateandoló a gusto.
4.  Si se modifica el _nombre del archivo_, debe corroborarse de agregar el mísmo nombre en todos los lugares donde se utilice el archivo.
5.  A continucación se especificará donde:
    - Debe dirigirse al archivo **streamlit_app.py**.
    - A la Sección:
      - ```
        # Cargar instrucciones y contenido base
        MATH_INSTRUCTIONS = cargar_texto("math_instructions.md")
        PRELIMINARES_MATEMATICA = cargar_texto("preliminares_matematica.md")
        ```
      - En este caso, dentro de los paréntesis, se debe modificar (**"preliminares_matematica.md"**) por el nombre del nuevo archivo cargado.

### 4.3 Modificar archivo **math_instructions.md**:

1.  Debe dirigirse al archivo con ese nombre.
2.  Una vez dentro, puede dirigirse a cualquier bloque del archivo y modificar su contenido, o, si se quiere, modificar el archivo entero con un nuevo contenido.
3.  La manera de modificar el contenido de este archivo se basa en dar instrucciones, como las que ya se encuentran cargadas en el, pero con nuevas directivas que seguirá el chatbot.
4.  Los prompts, instrucciones y directivas, están organizadas por títulos, subtítulos, listas, etc; de manera que pueda comprenderse facilmente, que sección es la que se debe modificar dependiendo que se quiera realizar.
5.  Se debe seguir el flujo actual y los bloques de como está dividido el archivo, para que el chatbot comprenda correctamente como debe responder y trabajar.
6.  Si se modifica el _nombre del archivo_, debe corroborarse de agregar el mísmo nombre en todos los lugares donde se utilice el archivo.
7.  A continucación se especificará donde:
    - Debe dirigirse al archivo **streamlit_app.py**.
    - A la seccion:
      - ```
        # Cargar instrucciones y contenido base
        MATH_INSTRUCTIONS = cargar_texto("math_instructions.md")
        PRELIMINARES_MATEMATICA = cargar_texto("preliminares_matematica.md")
        ```
      - En este caso, dentro de los paréntesis, se debe modificar (**"math_instructions.md"**) por el nombre del nuevo archivo cargado.

### 4.5 Modificar archivo streamlit_app.py:

1.  Dentro del archivo debe dirigirse a la sección de _"Cargar instrucciones y contenido base"_:
    - ```
      # Cargar instrucciones y contenido base
      MATH_INSTRUCTIONS = cargar_texto("math_instructions.md")
      PRELIMINARES_MATEMATICA = cargar_texto("preliminares_matematica.md")
      ```
2.  Dentro de los paréntesis, se debe especificar el nombre de los correspondientes archivos cargados, dependiendo si es un nuevo archivo de _instrucción_ o un nuevo _archivo base de información_.
3.  **_Importante_**

    - No debe modificarse el nombre de las variables "MATH_INSTRUCTIONS" y "PRELIMINARES_MATEMATICA", salvo que sea necesario y así se quiera.
      Esto debido a que la nueva información, prompts o instrucciones, seguirán funcionando correctamente por más que sea trate de un tema diferente.

4.  Si de todas maneras se desea modificar el nombre de las variables, puede hacerse, pero cambiando el mísmo en cada sección del código donde se utilice.
    A continucación se especificará donde.
    - Debe dirigirse a la seción de:
      - ```
           # Crear contexto inicial con instrucciones y contenido del libro
           initial_context = [
           {"role": "system", "content": "Es OBLIGATORIO que EVITES utilizar texto plano para las operaciones matemáticas, hasta en las operaciones matemáticas que escribas en texto plano y SIEMPRE debas usar formato LaTeX. Por ejemplo, $x^2 + 2x + 1 = 0$. Devuelve las ecuaciones matemáticas según las reglas establecidas."},
           {"role": "system", "content": MATH_INSTRUCTIONS},
           {"role": "assistant", "content": PRELIMINARES_MATEMATICA},
           ]
        ```
        Y modificar ["MATH_INSTRUCTIONS"] por el nuevo nombre de la variable o ["PRELIMINARES_MATEMATICA"] por el nuevo nombre de la variable.

#### Aplicar los cambios:

Después de modificar los archivos, presione el botón **"Commit changes"** (de color verde) y confirme los cambios realizados. Automáticamente, la aplicación se reiniciará con las modificaciones aplicadas.
