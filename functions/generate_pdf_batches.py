import os
import asyncio
import logging
import hashlib
import pandas as pd
from PyPDF2 import PdfReader


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFClient:
    def __init__(self):
        self.metadata = None

        self.U_HOME = os.getenv("HOME")
        self.dir_path = os.path.join(self.U_HOME, "Documents/home/knowledgebase/data")
        self.datalake_path = os.path.join(self.U_HOME, "Documents/home/knowledgebase/books/books")  # mostly pdfs, and the occasional other type
        self.text_dir = os.path.join(self.dir_path, "text_files")


        # Ensure the directory exists
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)      
                  
    async def get_bookpages(self):
        for root, dirs, files in os.walk(self.datalake_path):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        reader = PdfReader(file_path)
                        num_pages = len(reader.pages)
                        logging.info(f"Number of pages in {file_path}: {num_pages}")
                    else:
                        logging.warning(f"File not found: {file_path}")

    
    async def get_booktext(self):
        import datetime
        start_time = datetime.datetime.now()
        logging.info(f"Start time: {start_time}")


        book_list = []
        for root, dirs, files in os.walk(self.datalake_path):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        reader = PdfReader(file_path)
                        book_text = ""
                        for page in reader.pages:
                            book_text += page.extract_text()

                        # Save the text to a file
                        file_name = os.path.splitext(file)[0]
                        # text_file_path = os.path.join(self.text_dir, f"{file_name}.txt")
                        # Ensure the text directory exists
                        if not os.path.exists(self.text_dir):
                            os.makedirs(self.text_dir)
                        with open(f"{self.text_dir}/{file_name}.txt", "w", encoding="utf-8", errors="replace") as text_file:
                            text_file.write(book_text)
                            logging.info(f"Saved text to {file_name}")
                        # Optionally, you can also save the text to the book_list
                        book_list.append(book_text)
                    else:
                        logging.warning(f"File not found: {file_path}")


                    for book in book_list:
                        
                        pass
        



    def chunk_text(self, text, chunk_size):
        """Split text into chunks of specified size."""
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]



async def main():
    pdfClient = PDFClient()
    # await pdfClient.get_bookpages()
    await pdfClient.get_booktext()



if __name__ == "__main__":
    asyncio.run(main())
    print("Check the logs for more details")