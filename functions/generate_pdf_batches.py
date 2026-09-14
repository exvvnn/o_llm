import os
import asyncio
import logging
import datetime
from PyPDF2 import PdfReader
from dotenv import load_dotenv



load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

vault_path = "Users/sudo/.vaults/o_vault"
text_path = "/Users/sudo/.vaults/o_agent/data"

class PDFClient:
    def __init__(self, vault_path, text_path):
        self.metadata = None
        self.vault_path = vault_path # os.getenv("VAULT_DIR")
        self.text_dir = text_path
    

    async def get_bookpages(self):
        if not self.vault_path:
            logging.error("VAULT_DIR not set")
            return

        for root, dirs, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        reader = PdfReader(file_path)
                        num_pages = len(reader.pages)
                        logging.info(f"Number of pages in {file_path}: {num_pages}")
                    else:
                        logging.warning(f"File not found: {file_path}")

    # Everything Broken from here done starting now. 
    async def get_booktext(self):
        print("Getting Book Text")

        if not self.vault_path or not self.text_dir:
            logging.error("VAULT_DIR not set")
            return

        start_time = datetime.datetime.now()
        logging.info(f"Start time: {start_time}")

        book_list = []
        vault_book_dir = f"{self.vault_path}/Books" #/Users/sudo/.vaults/o_vault/Books
        logging.warning(vault_book_dir)

        for root, dirs, files in os.walk(vault_book_dir):
            dir_root = root
            dirss = dirs
            filess = files
            print(dir_root, dirss, filess)


            for file in files:
                if file.endswith(".pdf"):
                    book_was_found = False
                    try:
                        file_path = os.path.join(root, file)
                        if book_was_found:
                            logging.info(f"Book already processed: {file_path}")
                            continue
                        book_was_found = True
                    except Exception as e:
                        logging.error(f"Error processing {file}: {e}")
                        continue
                    
                    # And BookFound was true
                    if os.path.exists(file_path):
                        reader = PdfReader(file_path)

                        # TODO: this string can be changed to a dictionary with metadata, details, and book text
                        #   Pretest Notes: Strings here seem ok, but a data structure would improve encapsulation.
                        book_text = ""
                        for page in reader.pages:
                            book_text += page.extract_text()

                        file_name = os.path.splitext(file)[0]
                        os.makedirs(self.text_dir, exist_ok=True)

                        text_file_path = os.path.join(self.text_dir, f"{file_name}.txt")
                        with open(text_file_path, "w", encoding="utf-8", errors="replace") as text_file:
                            text_file.write(book_text)
                            logging.info(f"Saved text to {file_name}")

                        book_list.append(book_text)
                    else:
                        logging.warning(f"File not found: {file_path}")



    def chunk_text(self, text, chunk_size):
        """Split text into chunks of specified size."""
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


async def main():
    pdf_client = PDFClient(vault_path, text_path)
    print(f"Vault Path: {pdf_client.vault_path}, Text Directory: {pdf_client.text_dir}")

    await pdf_client.get_booktext()


if __name__ == "__main__":
    asyncio.run(main())
    print("Check the logs for more details")