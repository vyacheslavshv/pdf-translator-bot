import shutil
import uuid
import traceback
import undetected_chromedriver as uc

from tempfile import NamedTemporaryFile, TemporaryDirectory
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from time import sleep
from utils import kill_chrome_drivers, wait_for_file_download


def convert_to_docx(file_path):
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file, TemporaryDirectory() as tmp_dir:
        with open(file_path, "rb") as f:
            pdf_array = bytearray(f.read())
        tmp_file.write(pdf_array)
        tmp_file_path = tmp_file.name

        kill_chrome_drivers()

        options = uc.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": tmp_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        driver = uc.Chrome(options=options)
        try:
            driver.get("https://pdfocr.org")
            element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "file"))
            )
            sleep(3)
            element.send_keys(tmp_file_path)

            element = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.ID, "lang"))
            )
            sleep(1)
            element.click()

            select = Select(driver.find_element(By.ID, "lang"))
            sleep(1)
            select.select_by_visible_text('Arabic')

            element = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.ID, "upload"))
            )
            sleep(1)
            element.click()

            element = WebDriverWait(driver, 300).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="result"]/a'))
            )
            sleep(1)
            element.click()

            downloaded_file = wait_for_file_download(tmp_dir)
            final_file_name = str(uuid.uuid4()) + ".docx"
            shutil.copy(downloaded_file, final_file_name)
        except Exception:
            traceback.print_exc()
        finally:
            driver.quit()

        return final_file_name
