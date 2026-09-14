import os
import re
from PyPDF2 import PdfReader
from typing import Optional, Callable, Sequence

def extract_isbn_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            isbn_pattern = r'\b(?:ISBN(?::\s*)?)?([0-9]{13}|[0-9]{9}[0-9X])\b'
            isbn_match = re.search(isbn_pattern, text, re.IGNORECASE)

            if isbn_match:
                return isbn_match.group(0)
            else:
                return None
    except Exception as e:
         print(f"An error occurred: {e}")
         return None


# TODO: replace the path with an environment variable
for root, dirs, files in os.walk(os.path.expanduser('')):
    for file in files:
        if file.endswith('.pdf'):
            pdf_path = os.path.join(root, file)
            print(f"Processing {pdf_path}...")
            isbn = extract_isbn_from_pdf(pdf_path)
            if isbn:
                print(f"ISBN found: {isbn}")
            else:
                print("ISBN not found in the PDF.")

            with open(os.path.join(root, 'isbn_extracted.txt'), 'a') as f:
                if isbn:
                    f.write(f"{file}: {isbn}\n")
                else:
                    f.write(f"{file}: ISBN not found\n")
