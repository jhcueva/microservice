import io
import json
import os
import time
import unittest
from datetime import datetime
import tempfile

from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from fastapi import BackgroundTasks

from src.services.storage_service import DigitalOceanStorageService

from .api.responses import STATUS, Response
from .config.config import Config

SCREEN_SHOOT_FOLDER = os.path.join(os.getcwd(), 'screenshots')

do_s3 = DigitalOceanStorageService.Instance(region_name=Config().BUCKET_REGION, bucket_name=Config(
).BUCKET_NAME, access_key=Config().ACCESS_KEY, secret_key=Config().SECRET_KEY, with_cdn=True)


class AttestationMicroservice(unittest.TestCase):
    def __init__(self, methodName='runTest', user_name=None, password=None, image_name=None):
        super(AttestationMicroservice, self).__init__(methodName)
        self.user_name = user_name
        self.password = password
        self.image_name = image_name

    def setUp(self):
        # Setting up Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver with the specified options
        self.driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=chrome_options)
        self.driver.implicitly_wait(5)
        self.driver.get(Config().PROVIEW_CAQH_ORG_URL)

    def test_load_sign_in_page(self):
        try:
            WebDriverWait(self.driver, 8).until(
                EC.title_contains('CAQH ProView - Sign In'))
            return Response.toData(data={"message": "ok"}, status_code=STATUS.HTTP_200_OK)
        except Exception as e:
            print('Load sign-in page error: ', e)
            return Response.toError(
                message='Failed to load sign in page',
                status_code=STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                error=str(e)
            )

    def test_sign_in(self):
        load_sign_in = self.test_load_sign_in_page()
        if load_sign_in.status_code != STATUS.HTTP_200_OK:
            return load_sign_in

        driver = self.driver

        try:
            user_name = driver.find_element(By.ID, 'UserName')
            password = driver.find_element(By.ID, 'Password')
            submit_btn = driver.find_element(
                By.XPATH, "//button[text()='Sign In']")

            user_name.send_keys(self.user_name)
            password.send_keys(self.password)
            submit_btn.click()

            try:
                error_sign_in = driver.find_element(
                    By.XPATH, "//div[@class='validation-summary-errors']/ul/li")
                if error_sign_in:
                    return Response.toError(
                        message='Invalid Username or Password. Please verify your information and try again.',
                        status_code=STATUS.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            except:
                pass

            try:
                WebDriverWait(self.driver, 8).until(
                    EC.title_contains('CAQH ProView - Home'))
            except Exception as e:
                print(f"Redirect to Home error: {e}")
                return Response.toError(
                    message="It's possible that the Username or Password are invalid.",
                    status_code=STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                    error=str(e)
                )

            return Response.toData(
                data={"message": "ok"},
                status_code=STATUS.HTTP_200_OK,
                message='Sign in success'
            )

        except Exception as e:
            print('Sign in error: ', e)
            return Response.toError(message=e, error=STATUS.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_review_and_attest(self):
        sign_in_response = self.test_sign_in()
        if sign_in_response.status_code != STATUS.HTTP_200_OK:
            return sign_in_response

        driver = self.driver

        try:
            # Wait until the link with text "Review & Attest" is present in the DOM
            review_and_attest = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[.//strong[text()='Review & Attest']]"))
            )
            review_and_attest.click()
        except Exception as e:
            return Response.toError(
                message='An error occur while clicking on Review & Attest',
                status_code=STATUS.HTTP_500_INTERNAL_SERVER_ERROR,
                error=str(e)
            )

        try:
            view_error = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//a[text()='View Errors']")))
            view_error.click()
            time.sleep(3)

            file_name = self.image_name + '.png'
            self.driver.set_window_size(1920, 1080)

            print('Start screenshot')
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tempfile_image:
                driver.save_screenshot(tempfile_image.name)
                driver.quit()

                result = {"message": "ok"}

                # Read the image content into memory
                with open(tempfile_image.name, 'rb') as image_file:
                    image_bytes = image_file.read()

                    # Return the file content as an image response
                    # return StreamingResponse(
                    #     iter([image_bytes]),
                    #     media_type="image/png",  # Adjust media type as necessary
                    # )
                    return Response(content=image_bytes, headers=result, media_type="image/png")

        except:
            pass

        file_name = self.image_name + '.png'
        self.driver.set_window_size(1920, 1080)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tempfile_image:
            driver.save_screenshot(tempfile_image.name)
            response = do_s3.upload_public_file(
                tempfile_image.file.read(), file_name)
            print(response)

        return Response.toData(
            message='Attest check success',
            status_code=STATUS.HTTP_200_OK,
            data={"screenshot": file_name}
        )

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main(verbosity=2)
