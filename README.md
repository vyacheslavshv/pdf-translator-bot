# PDF Translator Bot

This Telegram bot is designed to help users translate PDF, EPUB, and MOBI documents. It uses a combination of Python libraries and external tools to process documents, convert them to DOCX for better translation handling, and then convert them back to PDF. The bot also adds a transparent watermark to the final PDF to ensure the translated documents are marked. The project leverages Calibre for file conversion, Selenium for interacting with online OCR services, and PyMuPDF for PDF manipulations.

## Project Structure

- `main.py`: Main executable script that runs the Telegram bot.
- `convert_to_docx.py`: Handles conversion of PDF files to DOCX format.
- `convert_to_pdf.py`: Converts translated DOCX files back to PDF.
- `translate.py`: Manages the translation of documents using online tools.
- `utils.py`: Contains utility functions for compression, watermarking, and more.
- `config.ini`: Configuration file for Telegram API keys and bot settings.
- `requirements.txt`: Lists all Python dependencies required to run the bot.
- `watermark.png`: Image file used as a watermark in translated PDF documents.

## Installation

### Prerequisites

Before you start, ensure you have Python 3.6+ installed. You will also need a Telegram bot token, which you can obtain by registering a new bot with the Telegram BotFather.

### System Dependencies

Certain functionalities of this bot require system packages:

```bash
sudo apt install calibre
```

### Setup Instructions

1. **Clone the repository**:

```bash
git clone https://github.com/vyacheslavshv/pdf-translator-bot.git
cd pdf-translator-bot
```

2. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure the bot**:

Fill in your API keys and bot token in `config.ini`.

```ini
[Telegram]
API_ID = your_api_id
API_HASH = your_api_hash
BOT_TOKEN = your_bot_token
```

4. **Run the bot**:

```bash
python main.py
```

## Usage

Send a PDF, EPUB, or MOBI file to the Telegram bot. It will process the file, translate it into your desired language, and send back a watermarked PDF version of the translated document.
