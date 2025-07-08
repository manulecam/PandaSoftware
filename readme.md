# ⚕️ Automatización de Gestión de Clientes e Información Administrativa #

🗃️ Este repositorio contiene un script Python diseñado para automatizar y agilizar el proceso de carga de información en un portal web de gestión de clientes. Orientado a optimizar la eficiencia en tareas administrativas recurrentes, el programa permite tramitar recetas de múltiples pacientes de forma secuencial y robusta.

💻 Desarrollado para un rol administrativo, este software es un "asistente digital" para la gestión de clientes, liberando tiempo valioso y reduciendo la carga de trabajo manual.

🛠️ Lenguajes y herramientas: Python y Selenium.

---

## Características Destacadas ⚙️

* **Acceso Automatizado:** Inicio de sesión seguro y automatizado en el portal web.
* **Procesamiento por Lotes:** Capacidad para procesar automáticamente una lista de códigos de clientes desde un archivo de texto (`codigos.txt`).
* **Carga de Datos de Clientes:** Ingreso automatizado del número de beneficiario y espera inteligente de la carga de sus datos en el sistema.
* **Selección de Información Modelo:** Identificación y aplicación de información estructurada y predefinidas disponible en el portal.
* **Gestión de Datos Específicos:** Completado automatizado de campos cruciales con información específica, numeros puntuales y otros detalles.
* **Manejo Dinámico de Diagnósticos:** Integra la información de diagnósticos (proveniente de una fuente externa al script) en el proceso de carga.
* **Generación de Informes:** Tramitación final y generación de informes pertinentes en el portal.
* **Manejo Inteligente de Pop-ups:** Gestión automática de diversas ventanas emergentes (advertencias, confirmaciones, etc.).
* **Registro Detallado (Logging):** Un sistema de registro exhaustivo que documenta cada paso, advertencia y error del proceso para una trazabilidad completa.
* **Captura de Pantallas en Errores:** Generación automática de capturas de pantalla en momentos críticos o ante errores inesperados, facilitando el diagnóstico visual.

---

## Flujo de Trabajo Automatizado 🤖

El script sigue una secuencia lógica y automatizada para cada paciente en la lista de `codigos.txt`:

1.  **Inicio y Carga de Configuración:** El script inicia una instancia del navegador Chrome y carga las credenciales de acceso al portal y la ruta de ChromeDriver desde el archivo `config.ini`.
2.  **Login en el Portal:** Accede a la URL de login del portal y realiza el inicio de sesión con las credenciales obtenidas.
3.  **Lectura de Clientes:** Se carga la lista de códigos de clientes a procesar desde el archivo `codigos.txt`.
4.  **Procesamiento por Cliente (Bucle):** Para cada código de paciclienteente en la lista:
    * **Ingreso de Beneficiario:** El código del cliente es ingresado en el campo correspondiente del portal y se espera la carga de sus datos.
    * **Recopilación de Información Modelo:** Se abre la lista de "Información Modelo" del cliente y se identifican toda la información estructurada y predefinida disponible (el identificador `data-pos` es clave para esta selección dinámica).
    * **Procesamiento por Información Modelo:** Por cada información modelo encontrada:
        * Se vuelve a ingresar el beneficiario (ya que la página puede reiniciarse o refrescarse).
        * Se selecciona la información modelo específica.
        * Se gestionan pop-ups de advertencia (si aparecen).
        * Se verifica la integridad de la información y se elimina si hay algo incompleto.
        * Se marcan casillas de confirmación y se selecciona la duración del alta de determinados servicios.
        * Se verifica la aparición de advertencias, registrando los códigos afectados en `errordiab.txt` y gestionando sus pop-ups.
        * Se manejan los pop-ups finales de confirmación o de excedencia para completar la tramitación.
        * Finalmente, se vuelve a la página principal para continuar con la siguiente información modelo o el siguiente cliente.
5.  **Finalización:** Una vez procesados todos los clientes de la lista, el script muestra una notificación emergente indicando la finalización exitosa.

---
