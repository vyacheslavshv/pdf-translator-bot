import os
import configparser
import asyncio
import traceback

from asyncio import CancelledError
from telethon import TelegramClient, events
from translate import translate_docx
from utils import epub2pdf, mobi2pdf, add_watermark_to_pdf
from convert_to_docx import convert_to_docx
from convert_to_pdf import convert_to_pdf

config = configparser.ConfigParser()
config.read("config.ini")

API_ID = config['Telegram']['API_ID']
API_HASH = config['Telegram']['API_HASH']
BOT_TOKEN = config['Telegram']['BOT_TOKEN']

MAX_PDF_SIZE = 15 * 1024 * 1024
MAX_DOCX_SIZE = 10 * 1024 * 1024
MAX_TRANSLATED_DOCX_SIZE = 5 * 1024 * 1024

task_queue = asyncio.Queue()


async def process_file(event):
    file_paths = []
    try:
        await asyncio.wait_for(process_file_core(event, file_paths), timeout=300)
    except asyncio.TimeoutError:
        await event.respond("Processing timed out. Please try again or use a smaller file.")
    except Exception:
        traceback.print_exc()
        await event.respond("An error occurred when processing your document.")
    finally:
        for path in file_paths:
            if path and os.path.exists(path):
                os.remove(path)


async def process_file_core(event, file_paths):
    file_path = await event.download_media()
    file_paths.append(file_path)
    original_file_name = os.path.splitext(file_path)[0]

    if not file_path.endswith(".pdf"):
        await event.respond("We are only accepting PDF files at this time.")
        return
        await event.respond("Converting your document...")
        try:
            if file_path.endswith(".epub"):
                new_path = epub2pdf(file_path)
                file_paths.append(new_path)
                file_path = new_path
            elif file_path.endswith(".mobi"):
                new_path = mobi2pdf(file_path)
                file_paths.append(new_path)
                file_path = new_path
        except Exception:
            await event.respond("Converting your document failed. Try a PDF file.")
            traceback.print_exc()
            return

    if os.path.getsize(file_path) > MAX_PDF_SIZE:
        await event.respond("File is very large. Please try a smaller file.")
        return

    await event.respond("Converting your document to DOCX...")
    docx_path = convert_to_docx(file_path)
    file_paths.append(docx_path)

    if os.path.getsize(docx_path) > MAX_DOCX_SIZE:
        await event.respond("File is still very large. Please try a smaller file.")
        return

    await event.respond("Translating your document...")
    translated_docx_path = translate_docx(docx_path)
    file_paths.append(translated_docx_path)

    if os.path.getsize(translated_docx_path) > MAX_TRANSLATED_DOCX_SIZE:
        await event.respond("Unable to convert it to DOCX, sending it as is...")
        translated_docx_name = f"{original_file_name}_translated.docx"
        os.rename(translated_docx_path, translated_docx_name)
        file_paths.append(translated_docx_name)
        await event.reply(file=translated_docx_name)
        return

    await event.respond("Converting translated document back to PDF...")
    final_pdf_path = convert_to_pdf(translated_docx_path)
    file_paths.append(final_pdf_path)

    await event.respond("Adding watermark...")
    watermarked_pdf_path = add_watermark_to_pdf(final_pdf_path, "watermark.png")
    file_paths.append(watermarked_pdf_path)

    original_file_path = f"{original_file_name}.pdf"
    os.rename(watermarked_pdf_path, original_file_path)

    await event.respond("Sending translated document...")
    await event.reply(file=original_file_path)


async def worker():
    while True:
        event = await task_queue.get()
        try:
            await process_file(event)
        except Exception:
            traceback.print_exc()
        finally:
            task_queue.task_done()


def setup_handlers(client):
    @client.on(events.NewMessage())
    async def handle_any_message(event):
        if not event.document:
            await event.respond("Send me a PDF file and I'll translate its content for you!")
            return

        file_name = event.document.attributes[0].file_name if event.document.attributes else "Unknown"
        file_size = event.document.size

        supported_formats = ['.pdf', '.epub', '.mobi']
        if not any(file_name.endswith(ext) for ext in supported_formats):
            await event.respond("I only accept .pdf, .epub, and .mobi formats!")
            return

        if file_size > MAX_PDF_SIZE:
            await event.respond(
                f"This file is too large. "
                f"Please send a file smaller than {MAX_PDF_SIZE // (1024 * 1024)} MB!"
            )
            return

        await event.respond("Downloading your file...")

        await task_queue.put(event)


async def main():
    client = TelegramClient('data/bot', int(API_ID), API_HASH)
    await client.start(bot_token=BOT_TOKEN)

    worker_task = asyncio.create_task(worker())

    setup_handlers(client)

    try:
        await client.run_until_disconnected()
    except CancelledError:
        pass
    finally:
        worker_task.cancel()
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
