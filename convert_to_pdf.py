import shutil
import uuid
import traceback
import undetected_chromedriver as uc

from tempfile import NamedTemporaryFile, TemporaryDirectory
from selenium.webdriver.common.by import By
from utils import kill_chrome_drivers, wait_for_file_download, safe_click, safe_send_keys


def convert_to_pdf(file_path):
    with NamedTemporaryFile(suffix=".docx", delete=False) as tmp_file, TemporaryDirectory() as tmp_dir:
        with open(file_path, "rb") as f:
            docx_array = bytearray(f.read())
        tmp_file.write(docx_array)
        tmp_file_path = tmp_file.name

        kill_chrome_drivers()

        options = uc.ChromeOptions()
        chrome_path = '/usr/bin/google-chrome-stable'
        options.binary_location = chrome_path
        # options.add_argument("--headless")
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
            driver.get("https://pdfocr.org/word-pdf.html")

            print("Waiting for file upload area")
            safe_send_keys(driver, (By.ID, "file"), tmp_file_path)

            print("Waiting for upload button")
            safe_click(driver, (By.ID, "upload"))

            print("Waiting for download button")
            safe_click(driver, (By.XPATH, '//*[@id="result"]/a'), 300)

            downloaded_file = wait_for_file_download(tmp_dir)
            final_file_name = str(uuid.uuid4()) + ".pdf"
            shutil.copy(downloaded_file, final_file_name)

            return final_file_name
        except Exception:
            traceback.print_exc()
        finally:
            driver.quit()
