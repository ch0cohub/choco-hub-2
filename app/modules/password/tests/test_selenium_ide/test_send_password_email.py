from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=4):
    """
    Espera a que la página se cargue completamente.
    """
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_send_password_email():
    """
    Prueba para verificar el flujo de inicio de sesión.
    """
    driver = initialize_driver()  # Cambia a True para modo sin cabeza

    try:
        # Accede a la página principal
        driver.get("http://localhost:5000/")
        wait_for_page_to_load(driver)

        # Navega al formulario de inicio de sesión
        login_link = driver.find_element(By.LINK_TEXT, "Login")
        login_link.click()
        wait_for_page_to_load(driver)

        # Interactúa con el formulario
        reset_link = driver.find_element(By.LINK_TEXT, "Click here!")
        reset_link.click()
        wait_for_page_to_load(driver)

        email_input = driver.find_element(By.ID, "email")
        email_input.send_keys("pablofuas@gmail.com")

        submit_button = driver.find_element(By.CSS_SELECTOR, ".btn")
        submit_button.click()
        wait_for_page_to_load(driver)

        # (Opcional) Verifica que el inicio de sesión fue exitoso
        # success_message = driver.find_element(By.CLASS_NAME, "success-message")
        # assert "Success" in success_message.text

    except Exception as e:
        print(f"Error durante la ejecución del test: {e}")
    finally:
        # Cierra el navegador
        close_driver(driver)


# Llama al test
test_send_password_email()
