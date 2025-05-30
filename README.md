# Screen Text Capture

This Python script allows you to capture a portion of your screen, extract English text from it using OCR (Optical Character Recognition), and copy the extracted text to your clipboard.

## Features
- Select any region of your screen with your mouse.
- Extracts English text from the selected region using Tesseract OCR.
- Automatically copies the extracted text to your clipboard.

## Dependencies
- Python 3.7+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [mss](https://pypi.org/project/mss/)
- [Pillow](https://pypi.org/project/Pillow/)
- [pytesseract](https://pypi.org/project/pytesseract/)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) (system dependency)

You can install the Python dependencies with:

```bash
pip install -r requirements.txt
```

Or individually:

```bash
pip install PyQt5 mss Pillow pytesseract
```

You must also have Tesseract-OCR installed on your system. On Ubuntu/Debian:

```bash
sudo apt install tesseract-ocr
```

On Arch Linux:

```bash
sudo pacman -S tesseract
```

## Usage

1. Run the script:
   ```bash
   python screen_text_capture.py
   ```
2. Your screen will be captured and displayed. Use your mouse to select the region you want to extract text from.
3. The extracted text will be printed in the terminal and copied to your clipboard automatically.

## Notes
- The script works on X11 and may not work on Wayland or remote desktop sessions.
- Make sure Tesseract is installed and available in your system PATH.

## License
MIT 