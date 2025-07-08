# ⚕️ Automatización de Gestión de Prescripciones Médicas

Este repositorio contiene un script Python diseñado para automatizar y agilizar el proceso de carga de prescripciones médicas en un portal web de gestión de salud. Orientado a optimizar la eficiencia en tareas administrativas recurrentes, el programa permite tramitar recetas de múltiples pacientes de forma secuencial y robusta.

Desarrollado para un rol administrativo que asiste a profesionales, este software es tu "asistente digital" para la gestión de medicamentos, liberando tiempo valioso y reduciendo la carga de trabajo manual.

---

## Características Destacadas ✨

* **Acceso Automatizado:** Inicio de sesión seguro y automatizado en el portal web.
* **Procesamiento por Lotes:** Capacidad para procesar automáticamente una lista de códigos de pacientes desde un archivo de texto (`codigos.txt`).
* **Carga de Datos de Pacientes:** Ingreso automatizado del número de beneficiario y espera inteligente de la carga de sus datos en el sistema.
* **Selección de Recetas Modelo:** Identificación y aplicación de recetas predefinidas disponibles en el portal.
* **Gestión de Datos de Medicamentos:** Completado automatizado de campos cruciales como dosis, cantidades y otros detalles de la medicación.
* **Manejo Dinámico de Diagnósticos:** Integra la información de diagnóstico (proveniente de una fuente externa al script) en el proceso de carga.
* **Generación de Prescripciones:** Tramitación final y generación de las prescripciones en el portal.
* **Manejo Inteligente de Pop-ups:** Gestión automática de diversas ventanas emergentes (advertencias de dosis máxima, confirmaciones de alta de receta, etc.).
* **Registro Detallado (Logging):** Un sistema de registro exhaustivo que documenta cada paso, advertencia y error del proceso para una trazabilidad completa.
* **Captura de Pantallas en Errores:** Generación automática de capturas de pantalla en momentos críticos o ante errores inesperados, facilitando el diagnóstico visual.

---

## Flujo de Trabajo Automatizado 🤖

El script sigue una secuencia lógica y automatizada para cada paciente en la lista de `codigos.txt`:

1.  **Inicio y Carga de Configuración:** El script inicia una instancia del navegador Chrome y carga las credenciales de acceso al portal y la ruta de ChromeDriver desde el archivo `config.ini`.
2.  **Login en el Portal:** Accede a la URL de login del portal y realiza el inicio de sesión con las credenciales obtenidas.
3.  **Lectura de Pacientes:** Se carga la lista de códigos de pacientes a procesar desde el archivo `codigos.txt`.
4.  **Procesamiento por Paciente (Bucle):** Para cada código de paciente en la lista:
    * **Ingreso de Beneficiario:** El código del paciente es ingresado en el campo correspondiente del portal y se espera la carga de sus datos.
    * **Recopilación de Recetas Modelo:** Se abre la lista de "Recetas Modelo" del paciente y se identifican todas las recetas predefinidas disponibles (el identificador `data-pos` es clave para esta selección dinámica).
    * **Procesamiento por Receta Modelo:** Por cada receta modelo encontrada:
        * Se vuelve a ingresar el beneficiario (ya que la página puede reiniciarse o refrescarse).
        * Se selecciona la receta modelo específica.
        * Se gestionan pop-ups de advertencia de medicamentos (si aparecen).
        * Se verifica la integridad de la receta y se elimina si está incompleta.
        * Se marcan casillas como "Marca comercial" y se selecciona la duración de la prescripción (ej. "Tres Meses").
        * Se activa el botón para "GENERAR RECETA".
        * Se verifica la aparición de advertencias de diagnóstico (ej. para pacientes diabéticos), registrando los códigos afectados en `errordiab.txt` y gestionando sus pop-ups.
        * Se manejan los pop-ups finales de confirmación o de excedencia de dosis para completar la tramitación.
        * Finalmente, se vuelve a la página principal para continuar con la siguiente receta modelo o el siguiente paciente.
5.  **Finalización:** Una vez procesados todos los pacientes de la lista, el script muestra una notificación emergente indicando la finalización exitosa.

---

## Requisitos 📥

Para que este script funcione correctamente en tu sistema, necesitarás lo siguiente:

* **Python 3.x:** Asegúrate de tener una versión reciente de Python 3 instalada.
* **Google Chrome:** El navegador web Google Chrome debe estar instalado, ya que Selenium interactúa con él.
* **ChromeDriver:** El driver de Chrome compatible con tu versión de Google Chrome. Puedes descargarlo desde [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads). Asegúrate de descargarlo y guardarlo en una ubicación accesible.

---

## Configuración Inicial ⚙️

Sigue estos pasos para preparar el script para su ejecución:

1.  **Clona este repositorio:**
    ```bash
    git clone [https://github.com/tu_usuario/tu_repositorio.git](https://github.com/tu_usuario/tu_repositorio.git)
    cd tu_repositorio
    ```
2.  **Instala las dependencias de Python:**
    Es altamente recomendable usar un entorno virtual para gestionar las dependencias.
    ```bash
    python -m venv venv
    # En Windows
    .\venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    pip install selenium
    ```
3.  **Crea y edita `config.ini`:**
    Este archivo es esencial para las credenciales y la ruta de ChromeDriver. Si no existe, el script intentará crear una plantilla automáticamente al ejecutarse por primera vez.
    ```ini
    [PAMI]
    USUARIO = TU_USUARIO_DEL_PORTAL_WEB
    CONTRASENA = TU_CONTRASENA_DEL_PORTAL_WEB

    [SELENIUM]
    CHROMEDRIVER_PATH = D:/ruta/a/tu/chromedriver.exe ; EJEMPLO: C:/Users/TuUsuario/Descargas/chromedriver.exe
    ```
    * **`USUARIO` y `CONTRASENA`**: Reemplázalos con tus credenciales de acceso al portal web.
    * **`CHROMEDRIVER_PATH`**: Asegúrate de que esta ruta apunte exactamente al archivo `chromedriver.exe` que descargaste.

4.  **Crea y llena `codigos.txt`:**
    Este archivo contiene la lista de pacientes a procesar.
    * Crea un archivo llamado `codigos.txt` en la misma carpeta que el script principal.
    * Ingresa **un código numérico por línea** para cada paciente (de 8 a 10 dígitos).
    ```
    12345678
    9876543210
    ...
    ```

---

## Cómo Usar el Script ▶️

Una vez que hayas completado la configuración, ejecuta el script desde tu terminal (asegúrate de estar en el entorno virtual si lo creaste y activaste):

```bash
python tu_script_principal.py