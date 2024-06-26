import shutil
import uuid
import traceback
import unittest.mock as mock

with mock.patch("multiprocessing.Lock", return_value=object()):
    import undetected_chromedriver as uc

from tempfile import NamedTemporaryFile, TemporaryDirectory
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils import kill_chrome_drivers, wait_for_file_download, safe_click, safe_send_keys


def convert_to_docx(file_path):
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file, TemporaryDirectory() as tmp_dir:
        with open(file_path, "rb") as f:
            pdf_array = bytearray(f.read())
        tmp_file.write(pdf_array)

        kill_chrome_drivers()

        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument(f"--homedir={tmp_dir}")
        options.add_argument(f"--disk-cache-dir={tmp_dir}/cache-dir")
        options.add_argument(f"--data-path={tmp_dir}/data-path")
        options.add_experimental_option(
            "prefs", {"download.default_directory": tmp_dir}
        )

        driver = uc.Chrome(options=options, enable_cdp_events=True)

        try:
            print("Waiting for site load")
            driver.get("https://pdfocr.org")

            print("Waiting for file upload area")
            safe_send_keys(driver, (By.ID, "file"), tmp_file.name)

            print("Waiting for lang choice")
            safe_click(driver, (By.ID, "lang"))
            select_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "lang")))
            Select(select_element).select_by_visible_text('Arabic')

            print("Waiting for upload button")
            safe_click(driver, (By.ID, "upload"))

            print("Waiting for download button")
            safe_click(driver, (By.XPATH, '//*[@id="result"]/a'), 300)

            downloaded_file = wait_for_file_download(tmp_dir)
            final_file_name = str(uuid.uuid4()) + ".docx"
            shutil.copy(downloaded_file, final_file_name)

            return final_file_name
        except Exception:
            traceback.print_exc()
        finally:
            driver.quit()
