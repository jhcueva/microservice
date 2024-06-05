import os
import json
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from src.config.config import Config

def handler(event, context):
    try:
        user_name = event.get('user_name')
        password = event.get('password')
        image_name = event.get('image_name')

        if not user_name or not password or not image_name:
            return {
                'statusCode': 400,
                'body': 'Missing user_name, password, or image_name in the request'
            }

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(5)
        driver.get(Config().PROVIEW_CAQH_ORG_URL)

        # Sign-in process
        try:
            WebDriverWait(driver, 8).until(EC.title_contains('CAQH ProView - Sign In'))
            user_name_input = driver.find_element(By.ID, 'UserName')
            password_input = driver.find_element(By.ID, 'Password')
            submit_btn = driver.find_element(By.XPATH, "//button[text()='Sign In']")

            user_name_input.send_keys(user_name)
            password_input.send_keys(password)
            submit_btn.click()

            WebDriverWait(driver, 8).until(EC.title_contains('CAQH ProView - Home'))
        except Exception as e:
            driver.quit()
            return {
                'statusCode': 500,
                'body': f'Sign-in failed: {str(e)}'
            }

        # Navigate to "Review & Attest"
        try:
            review_and_attest = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[.//strong[text()='Review & Attest']]"))
            )
            review_and_attest.click()

            view_error = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='View Errors']"))
            )
            view_error.click()
            time.sleep(3)

            file_name = f"{image_name}.png"
            driver.set_window_size(1920, 1080)

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tempfile_image:
                driver.save_screenshot(tempfile_image.name)
                driver.quit()

                with open(tempfile_image.name, 'rb') as image_file:
                    image_bytes = image_file.read()

                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'image/png'},
                    'body': image_bytes,
                    'isBase64Encoded': True
                }
        except Exception as e:
            driver.quit()
            return {
                'statusCode': 500,
                'body': f'Error during attestation process: {str(e)}'
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Unhandled error: {str(e)}'
        }

if __name__ == "__main__":
    # Simulate a local event and context
    event = {
        "user_name": "your_username",
        "password": "your_password",
        "image_name": "screenshot"
    }
    context = {}
    response = handler(event, context)
    print(response)
