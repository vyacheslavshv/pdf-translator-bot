import os
import shutil
import uuid
import traceback
import undetected_chromedriver as uc

from tempfile import NamedTemporaryFile, TemporaryDirectory
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

from time import sleep, time
from utils import kill_chrome_drivers


def translate_pdf(pdf: bytearray):
    with NamedTemporaryFile(suffix=".docx", delete=False) as tmp_file, TemporaryDirectory() as tmp_dir:
        tmp_file.write(pdf)

        kill_chrome_drivers()

        options = uc.ChromeOptions()
        chrome_path = '/usr/bin/google-chrome-stable'
        options.binary_location = chrome_path
        options.add_argument("--headless")
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        )
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("prefs", {
            "download.default_directory": tmp_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        driver = uc.Chrome(options=options)
        try:
            print("Waiting for site load")
            driver.get("https://translate.google.com/?sl=auto&tl=en&op=docs")

            try:
                print("Waiting for 'Accept all cookies' to appear")
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Accept all')]"))
                ).click()
            except Exception:
                pass

            print("Waiting for file upload area")
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
            ).send_keys(tmp_file.name)

            print("Waiting for translate button")
            WebDriverWait(driver, 300).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Translate')]]"))
            ).click()

            print("Waiting for Download translation or Got it button")
            element = WebDriverWait(driver, 300).until(check_elements_clickable)
            if element.text == "Got it":
                print("Google is telling us to try again later")
                return b""
            element.click()

            max_wait = 300
            start_time = time()
            output_filename = os.path.join(tmp_dir, os.path.basename(tmp_file.name))

            while not os.path.exists(output_filename):
                if time() - start_time > max_wait:
                    raise Exception("Timeout reached: File download did not complete in time.")
                sleep(1)

            final_pdf_name = str(uuid.uuid4()) + ".docx"
            shutil.copy(output_filename, final_pdf_name)
        except Exception:
            traceback.print_exc()
        finally:
            driver.quit()

    return final_pdf_name


def translate_docx(file_name):
    try:
        with open(file_name, "rb") as f:
            file_content = bytearray(f.read())
        translated_file = translate_pdf(file_content)
        print("Done translating")

        return translated_file
    except Exception:
        traceback.print_exc()
        return


def check_elements_clickable(driver):
    paths: list[str] = [
        "//button[.//span[contains(text(), 'Download translation')]]",
        "//button[.//span[contains(text(), 'Got it')]]",
    ]
    for xpath in paths:
        try:
            element = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            if element:
                return element
        except WebDriverException:
            continue
    return
