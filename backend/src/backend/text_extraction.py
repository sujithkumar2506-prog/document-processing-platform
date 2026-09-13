import pdfplumber

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            # extract_text() preserves basic visual layout positioning
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text