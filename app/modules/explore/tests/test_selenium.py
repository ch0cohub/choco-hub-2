# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestSelenium():
  # este método se ejecuta antes de cada test y se encarga de inicializar el driver de selenium
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  # este método se ejecuta después de cada test y se encarga de cerrar el driver de selenium
  def teardown_method(self, method):
    self.driver.quit()
  
  # este es el test que se ejecutará con selenium, primero se accede a la ruta, se hace click en la barra de búsqueda, se escribe "sample"
  # y se presiona enter
  def test_selenium(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(1346, 748)
    self.driver.find_element(By.ID, "search-query").click()
    self.driver.find_element(By.ID, "search-query").send_keys("sample")
    self.driver.find_element(By.ID, "search-query").send_keys(Keys.ENTER)
  
# se crea una instancia de la clase TestSelenium y se llaman a los métodos de la clase
test = TestSelenium()
test.setup_method(None)
test.test_selenium()
test.teardown_method(None)

