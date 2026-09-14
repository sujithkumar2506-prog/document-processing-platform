import pdfplumber
import pytesseract
from pdf2image import convert_from_path

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\poppler-26.07.0\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            # extract_text() preserves basic visual layout positioning
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text


def extract_with_ocr(pdf_path):

    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    pages_text = []

    for image in images:
        page_text = pytesseract.image_to_string(image)
        pages_text.append(page_text)

    return "\n".join(pages_text)