import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )
  
def test_downloadall():
    driver = initialize_driver()
    
    try:
        host = get_host_for_selenium_testing()
        driver.get(f"{host}/")
        wait_for_page_to_load(driver)
        download_button=driver.find_element(By.LINK_TEXT, "Download all datasets!")
        wait_for_page_to_load(driver)
        download_button.click()

    finally:

        # Close the browser
        close_driver(driver)

test_downloadall()
    
    

  
