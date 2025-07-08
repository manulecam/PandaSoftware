from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException

import time
import os
import logging
import configparser
import tkinter as tk
from tkinter import messagebox

# --- Configuración del Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Cargar Configuración ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_script_dir, "config.ini")
config = configparser.ConfigParser()

if not os.path.exists(config_file_path):
    logger.critical(f"ERROR: Archivo de configuración '{config_file_path}' no encontrado.")
    logger.info("Creando 'config.ini' de ejemplo. Edítalo con tus credenciales y la ruta de ChromeDriver.")
    config['CREDENTIALS'] = {'USERNAME': 'TU_USUARIO', 'PASSWORD': 'TU_CONTRASENA'}
    config['SELENIUM'] = {'CHROMEDRIVER_PATH': 'D:/ruta/a/chromedriver.exe'}
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    logger.critical("Script detenido. Por favor, edita 'config.ini' y reinicia.")
    exit()

config.read(config_file_path)

try:
    chrome_driver_path = config['SELENIUM']['CHROMEDRIVER_PATH']
    portal_user = config['CREDENTIALS']['USERNAME']
    portal_pass = config['CREDENTIALS']['PASSWORD']
except KeyError as e:
    logger.critical(f"Error en config.ini: Falta la sección o clave '{e}'.")
    exit()

# --- Funciones Auxiliares ---
def take_screenshot(driver, item_id, stage):
    """Guarda una captura de pantalla en 'screenshots'."""
    screenshots_dir = os.path.join(current_script_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    filename = f"error_{item_id}_{stage}_{int(time.time())}.png"
    filepath = os.path.join(screenshots_dir, filename)
    try:
        driver.save_screenshot(filepath)
        logger.info(f"Captura guardada en: {filepath}")
    except Exception as e:
        logger.error(f"No se pudo tomar captura: {e}")

def enter_item_id(driver, item_id):
    """Ingresa un ID y espera que datos asociados se carguen."""
    logger.info(f"Ingresando ID: {item_id}")
    id_field = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "generic_id_field"))) # GENERALIZADO
    id_field.clear()
    id_field.send_keys(item_id)
    id_field.send_keys(Keys.TAB)
    try:
        # Esperar a que un campo dependiente se cargue y un botón importante esté visible
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.ID, "loaded_data_field").get_attribute("value").strip() != "" and \
                      d.find_element(By.ID, "process_button").is_displayed()
        )
        logger.info("Datos asociados al ID cargados.")
    except TimeoutException:
        logger.warning(f"Timeout esperando carga de datos para ID {item_id}.")
        take_screenshot(driver, item_id, "data_load_timeout")

def select_model_entry(driver, model_identifier, iframe_css_selector):
    """Abre un pop-up de selección de modelo y elige una entrada."""
    logger.info("Abriendo lista de Modelos...")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "process_button"))).click() # GENERALIZADO
    
    logger.info(f"Cambiando a iframe: {iframe_css_selector}")
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, iframe_css_selector)))
    logger.info("Dentro del iframe de modelos.")

    try:
        xpath_model_entry = f"//tr[@class='rowModel' and @data-pos='{model_identifier}']" # GENERALIZADO
        clickable_entry = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, xpath_model_entry)))
        clickable_entry.click()
        logger.info(f"Clic en entrada de modelo (identifier='{model_identifier}') realizado.")
        driver.switch_to.default_content()
        logger.info("Contexto cambiado de vuelta al contenido principal.")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "main_item_field_1"))) # GENERALIZADO
        logger.info("Campo principal visible, modelo cargado.")
        return True
    except Exception as e:
        logger.error(f"Error al seleccionar modelo '{model_identifier}': {e}")
        take_screenshot(driver, f"item_id_unknown_model_{model_identifier}", "select_model_error")
        driver.switch_to.default_content()
        logger.info("Contexto cambiado de vuelta al contenido principal después de error en selección de modelo.")
        return False
    finally:
        driver.switch_to.default_content()

def verify_and_delete_incomplete_entry(driver, item_id):
    """Verifica y elimina entradas incompletas según condiciones."""
    entry_deleted = False
    entry_sections = {
        1: {"field1_id": "main_item_field_1", "field2_id": "main_quantity_field_1", "delete_js_func": "process.deleteEntry(1)"}, # GENERALIZADO
    }
    for num, ids in entry_sections.items():
        logger.info(f"Verificando entrada en sección {num}...")
        try:
            val1 = WebDriverWait(driver, 0.5).until(EC.visibility_of_element_located((By.ID, ids["field1_id"]))).get_attribute("value").strip()
            val2 = driver.find_element(By.ID, ids["field2_id"]).get_attribute("value").strip()
            if not val1 and not val2:
                logger.warning(f"Entrada incompleta detectada en sección {num} para ID {item_id}. Eliminando.")
                driver.execute_script(ids["delete_js_func"])
                logger.info(f"Función JS '{ids['delete_js_func']}' ejecutada.")
                entry_deleted = True
                time.sleep(1.5)
        except (TimeoutException, NoSuchElementException):
            logger.debug(f"Campos de entrada en sección {num} no visibles/accesibles.")
        except Exception as e:
            logger.error(f"Error al verificar/eliminar entrada {num} para ID {item_id}: {e}")
            take_screenshot(driver, item_id, f"delete_entry_{num}_error")
    return entry_deleted

def handle_popups(driver, item_id, popup_type="post_generate"):
    """Maneja varios tipos de pop-ups."""
    # Lógica simplificada: busca y clickea botones genéricos
    # (Se eliminan los XPATHS específicos para simplificar y desidentificar)
    try:
        # Ejemplo: pop-up de confirmación general
        confirm_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirmar')]")))
        confirm_button.click()
        logger.info("Pop-up de confirmación general manejado.")
        time.sleep(1)
        return True
    except TimeoutException:
        pass
    except Exception as e:
        logger.warning(f"Error al manejar pop-up genérico: {e}")
        take_screenshot(driver, item_id, f"generic_popup_error_{popup_type}")
    return False

# --- Inicio del Programa ---
driver = None
try:
    logger.info(f"Usando ChromeDriver desde: {chrome_driver_path}")
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    login_url = "https://example.com/login" # URL GENERALIZADA
    logger.info(f"Abriendo la página de login: {login_url}")
    driver.get(login_url)
    driver.maximize_window()

    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "username_field"))).send_keys(portal_user) # GENERALIZADO
    logger.info("Usuario ingresado.")
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "password_field"))).send_keys(portal_pass) # GENERALIZADO
    logger.info("Contraseña ingresada.")
    time.sleep(1)

    driver.find_element(By.ID, "password_field").send_keys(Keys.ENTER) # GENERALIZADO
    logger.info("Login enviado. Esperando página principal...")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "main_dashboard_field"))) # GENERALIZADO
    logger.info("Página principal detectada.")

    codes_file_path = os.path.join(current_script_dir, "codigos.txt")
    item_ids = []
    try:
        with open(codes_file_path, "r") as f:
            item_ids = [line.strip() for line in f if line.strip()]
        if not item_ids:
            logger.warning("El archivo codigos.txt está vacío.")
        else:
            logger.info(f"Se encontraron {len(item_ids)} IDs a procesar.")
    except FileNotFoundError:
        logger.critical(f"Archivo 'codigos.txt' no encontrado en '{codes_file_path}'.")
        if driver: driver.quit()
        exit()

    iframe_model_selector = "iframe[src*='modelController.php']" # GENERALIZADO

    for current_item_id in item_ids:
        logger.info(f"\n===== INICIANDO PROCESO PARA ID: {current_item_id} =====")
        try:
            enter_item_id(driver, current_item_id)
            
            model_identifiers_list = []
            logger.info("Recopilando identificadores de modelos...")
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "process_button"))).click() # GENERALIZADO
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, iframe_model_selector)))
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//tr[@class='rowModel']"))) # GENERALIZADO
                model_rows = driver.find_elements(By.XPATH, "//tr[@class='rowModel']") # GENERALIZADO
                for row in model_rows:
                    data_pos = row.get_attribute("data-pos")
                    if data_pos: model_identifiers_list.append(data_pos)
                logger.info(f"Se encontraron {len(model_identifiers_list)} modelos para ID {current_item_id}.")
            finally:
                driver.switch_to.default_content()
                logger.info("Vuelto al contenido principal después de recopilar IDs.")

            try:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                logger.info("Tecla ESCAPE presionada para cerrar pop-up de modelos."); time.sleep(1)
            except Exception:
                logger.debug("No se pudo cerrar pop-up de modelos con Escape (quizás ya estaba cerrado).")

            if not model_identifiers_list:
                logger.info(f"No hay modelos para procesar para {current_item_id}. Pasando al siguiente.")
                continue

            for model_id in model_identifiers_list:
                logger.info(f"\n--- ID {current_item_id}: Procesando Modelo '{model_id}' ---")
                enter_item_id(driver, current_item_id)
                if not select_model_entry(driver, model_id, iframe_model_selector):
                    logger.warning(f"No se pudo seleccionar modelo '{model_id}' para {current_item_id}. Saltando al siguiente.")
                    continue

                handle_popups(driver, current_item_id, "warning_medication") # GENERALIZADO
                verify_and_delete_incomplete_entry(driver, current_item_id)
                
                # Campos de selección y botón de generación - GENERALIZADOS
                try:
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "checkbox_generic_1"))).click() # GENERALIZADO
                    logger.info("Checkbox procesado.")
                    time.sleep(1)
                    Select(WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "dropdown_generic_1")))).select_by_visible_text("Opción Predeterminada") # GENERALIZADO
                    logger.info("Opción seleccionada.")
                    time.sleep(1)
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "generate_button"))).click() # GENERALIZADO
                    logger.info("Botón 'GENERAR' clickeado.")
                except TimeoutException:
                    logger.error(f"Timeout al procesar campos/botón generar para {current_item_id}, modelo {model_id}.")
                    take_screenshot(driver, current_item_id, f"generate_timeout_mid_process_m{model_id}")
                    continue
                except Exception as e_gen:
                    logger.error(f"Error al procesar campos/botón generar para {current_item_id}, modelo {model_id}: {e_gen}")
                    take_screenshot(driver, current_item_id, f"generate_error_mid_process_m{model_id}")
                    continue

                handle_popups(driver, current_item_id, "general_warning") # GENERALIZADO
                handle_popups(driver, current_item_id, "success_popup") # GENERALIZADO

                # Botón de volver - GENERALIZADO
                try:
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "back_button"))).click() # GENERALIZADO
                    logger.info("Botón 'Volver' clickeado.")
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "generic_id_field"))) # GENERALIZADO
                    logger.info("Página recargada para siguiente ID.")
                    time.sleep(1.5)
                except Exception as e_back:
                    logger.critical(f"Error al volver o recargar página para {current_item_id}: {e_back}. No se puede continuar.")
                    take_screenshot(driver, current_item_id, "back_button_error")
                    break

                logger.info(f"--- Fin de la iteración para ID {current_item_id}, modelo '{model_id}' ---")
            
            logger.info(f"Proceso de {len(model_identifiers_list)} modelo(s) completado para el ID {current_item_id}.")

        except Exception as e_item_id:
            logger.error(f"===== ERROR INESPERADO PROCESANDO AL ID {current_item_id}: {e_item_id} =====")
            take_screenshot(driver, current_item_id, "item_process_error")
            try:
                logger.info("Intentando recargar la página principal para recuperarse del error...")
                driver.get("https://example.com/main_page") # URL GENERALIZADA
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "main_dashboard_field"))) # GENERALIZADO
                logger.info("Página principal recargada con éxito.")
            except Exception as e_reload:
                logger.critical(f"No se pudo recargar la página principal después de un error con ID {current_item_id}: {e_reload}")
                logger.critical("El script no puede continuar de forma segura. Finalizando.")
                if driver: take_screenshot(driver, current_item_id, "reload_fail_after_error")
                raise
            logger.info(f"Saltando al siguiente ID si hay más...")

    logger.info("\n\n===== TODOS LOS IDs DEL ARCHIVO HAN SIDO PROCESADOS =====")

    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Proceso Finalizado", "La automatización ha sido finalizada con éxito.")
    except Exception as e_popup:
        logger.error(f"Error al intentar mostrar la ventana emergente de finalización: {e_popup}")

except Exception as e_general_script:
    logger.critical(f"Ocurrió un error general e inesperado en el script: {e_general_script}")
    if driver: take_screenshot(driver, "global", "general_error")
finally:
    logger.info("Script finalizado. El navegador permanecerá abierto para revisión.")
    # Si quieres que el navegador se cierre automáticamente al finalizar, descomenta la siguiente línea:
    # if 'driver' in locals() and driver is not None:
    #     driver.quit()