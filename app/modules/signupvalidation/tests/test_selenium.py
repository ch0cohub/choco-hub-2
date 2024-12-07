from selenium.common.exceptions import NoSuchElementException
import time

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_signupvalidation_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()
    

        # Open the index page
        driver.get(f'{host}/signup/')
        wait_for_page_to_load(driver)

        
        email_field = driver.find_element(By.ID, 'email')
        name_field = driver.find_element(By.ID, "name")
        surname_field = driver.find_element(By.ID, "surname")
        password_field = driver.find_element(By.ID, "password")
        
        name_field.send_keys("pepe")
        surname_field.send_keys("pepe")
        email_field.send_keys("pepepepe13@gmail.com")
        password_field.send_keys("pepe")
        
        
        
        driver.find_element(By.ID, "submit").click()

        # Wait a little while to make sure the page has loaded completely
     


    finally:

        # Close the browser
        close_driver(driver)


# Call the test function
test_signupvalidation_index()



