import os
import fitz
import subprocess
from time import time, sleep


def add_watermark_to_pdf(pdf_path, watermark_image):
    doc = fitz.open(pdf_path)
    watermark = fitz.open(watermark_image)

    for page in doc:
        rect = page.rect
        pixmap = watermark[0].get_pixmap()
        x = (rect.width - pixmap.width) / 2
        y = (rect.height - pixmap.height) / 2
        image_rect = fitz.Rect(x, y, x + pixmap.width, y + pixmap.height)
        page.insert_image(image_rect, pixmap=pixmap, overlay=False)

    output_path = pdf_path.replace(".pdf", "_watermarked.pdf")
    doc.save(output_path)
    doc.close()
    return output_path


def kill_chrome_drivers():
    try:
        subprocess.check_call("pkill chromedriver", shell=True)
        subprocess.check_call("pkill chrome", shell=True)
    except subprocess.CalledProcessError:
        pass


def epub2pdf(epub_path):
    output_pdf_path = epub_path.replace('.epub', '.pdf')
    command = [
        'ebook-convert', epub_path, output_pdf_path,
        '--pdf-page-numbers', '--paper-size', 'a4',
        '--pdf-default-font-size', '16', '--pdf-mono-font-size', '12'
    ]
    subprocess.run(command, check=True)
    return output_pdf_path


def mobi2pdf(mobi_path):
    output_pdf_path = mobi_path.replace('.mobi', '.pdf')
    command = [
        'ebook-convert', mobi_path, output_pdf_path,
        '--pdf-page-numbers', '--paper-size', 'a4',
        '--pdf-default-font-size', '16', '--pdf-mono-font-size', '12'
    ]
    subprocess.run(command, check=True)
    return output_pdf_path


def wait_for_file_download(directory, timeout=300):
    start_time = time()
    while True:
        try:
            files = [f for f in os.listdir(directory) if not f.endswith('.crdownload')]
            if files:
                full_path = os.path.join(directory, files[0])
                if os.path.isfile(full_path):
                    current_size = os.path.getsize(full_path)
                    sleep(1)
                    new_size = os.path.getsize(full_path)
                    if current_size == new_size:
                        return full_path
        except Exception:
            pass

        if time() - start_time > timeout:
            raise TimeoutError("File download did not complete in time")
