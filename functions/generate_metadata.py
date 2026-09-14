import os
import asyncio
import logging
from pathlib import Path
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PDFClient:
    def __init__(self):
        self.U_HOME = os.getenv("HOME")
        self.dir_path = os.path.join(self.U_HOME, os.getenv("METADATA_PATH", ".metadata"))
        repository_root = Path(__file__).resolve().parents[2]
        default_book_path = repository_root / "o_vault" / "Books"
        configured_book_path = os.getenv("BOOK_PATH")
        if configured_book_path:
            expanded_book_path = os.path.expandvars(os.path.expanduser(configured_book_path))
            self.datalake_path = (
                expanded_book_path
                if "$" not in expanded_book_path
                else str(default_book_path)
            )
        else:
            self.datalake_path = str(default_book_path)
        self.metadata = None

        os.makedirs(self.dir_path, exist_ok=True)
        logging.info("Using book corpus path: %s", self.datalake_path)

    async def write_metadata(self):
        metadata_file = os.path.join(self.dir_path, "folder_metadata.txt")
        logging.info(f"Writing metadata to: {metadata_file}")

        with open(metadata_file, "w") as file:
            for root, dirs, files in os.walk(self.datalake_path):
                for filename in files:
                    if filename.endswith(".pdf"):
                        file_path = os.path.join(root, filename)
                        if os.path.exists(file_path):
                            reader = PdfReader(file_path)
                            metadata = reader.metadata
                            file.write(str(metadata) + "\n")
                            logging.info(f"Metadata written for: {file_path}")
                        else:
                            logging.warning(f"File not found: {file_path}")

        return metadata_file

    async def read_metadata(self):
        for root, dirs, files in os.walk(self.datalake_path):
            for filename in files:
                if filename.endswith(".pdf"):
                    file_path = os.path.join(root, filename)
                    if os.path.exists(file_path):
                        reader = PdfReader(file_path)
                        metadata = reader.metadata
                        self.metadata = str(metadata)
                        logging.info(f"Metadata read for: {file_path}")

                        for key, value in metadata.items():
                            if key == "/Title":
                                logging.info(f"Title: {value}")
                            if key == "/Author":
                                logging.info(f"Author: {value}")
                            if key == "/CreationDate":
                                logging.info(f"Creation date: {value}")
                    else:
                        logging.warning(f"File not found: {file_path}")

    async def extract_text(self, output_dir=None):
        """Extract page-aware text from PDFs into one UTF-8 file per PDF."""
        if output_dir is None:
            output_dir = os.path.join(self.dir_path, "pdf_text")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        extracted_files = []

        for root, dirs, files in os.walk(self.datalake_path):
            for filename in sorted(files):
                if not filename.lower().endswith(".pdf"):
                    continue

                file_path = Path(root) / filename
                if not file_path.exists():
                    logging.warning("File not found: %s", file_path)
                    continue

                destination = output_path / f"{file_path.stem}.txt"
                try:
                    reader = PdfReader(str(file_path))
                    with destination.open("w", encoding="utf-8") as output:
                        output.write(f"SOURCE: {file_path}\n")
                        output.write(f"TITLE: {(reader.metadata or {}).get('/Title', file_path.stem)}\n\n")
                        for page_number, page in enumerate(reader.pages, start=1):
                            text = (page.extract_text() or "").strip()
                            if not text:
                                logging.warning("No text found on %s page %d", file_path, page_number)
                                continue
                            output.write(f"--- Page {page_number} ---\n")
                            output.write(text)
                            output.write("\n\n")
                    extracted_files.append(str(destination))
                    from o_db.storage import save_document

                    save_document(
                        source_path=str(file_path),
                        title=(reader.metadata or {}).get("/Title", file_path.stem),
                        content=destination.read_text(encoding="utf-8"),
                    )
                    logging.info("Text extracted: %s", file_path)
                except Exception as error:
                    logging.warning("Could not extract %s: %s", file_path, error)

        return extracted_files


from argparse import ArgumentParser

argparser = ArgumentParser(description="Simple PDF metadata generator.")

async def main():
    pdf_client = PDFClient()
    await pdf_client.write_metadata()
    await pdf_client.read_metadata()
    await pdf_client.extract_text()

    async def Parser(argparser=None):
        



if __name__ == "__main__":
    asyncio.run(main())
    print("Check the logs for more details")