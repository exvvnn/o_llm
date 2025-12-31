# Process inputs:
"""
    #TODO
"""

# Python Dependencies
import os
import asyncio
import logging
import hashlib

# Module Dependencies
from PyPDF2 import PdfReader
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file, and prepare PDF client
load_dotenv()
pdfClient = PDFClient()

METADATA_PATH = os.getenv("DATALAKE_PATH")


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




# Class inheritance:
class PDFClient:
    def __init__(self):
        self.U_HOME = os.getenv("HOME")
        self.dir_path = os.path.join(self.U_HOME, METADATA_PATH)
        self.datalake_path = os.path.join(self.U_HOME, "Documents/home/knowledgebase/books/books")  # mostly pdfs, and the occasional other type
        self.metadata = Optional[]
        self.headers = None
        self.body = None

        # Ensure the directory exists
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    async def write_metadata(self):
        print(f"Writing metadata to folder: {os.path.join(self.dir_path, 'folder_metadata.txt')}")
        with open(os.path.join(self.dir_path, "folder_metadata.txt"), "w") as file:
            for root, dirs, files in os.walk(self.datalake_path):
                for coll in files:
                    if coll.endswith(".pdf"):
                        file_path = os.path.join(root, coll)
                        if os.path.exists(file_path):
                            reader = PdfReader(file_path)
                            metadata = reader.metadata
                            metadata_str = str(metadata)
                            file.write(metadata_str + "\n")
                            # pd.read_csv(metadata_str)
                            logging.info(f"Metadata written for file: {file_path}")
                        else:
                            logging.warning(f"File not found: {file_path}")

        return os.path.join(self.dir_path, "folder_metadata.txt")

    async def read_metadata(self):
        for root, dirs, files in os.walk(self.datalake_path):
            for file in files:
                if file.endswith(".pdf"):
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        reader = PdfReader(file_path)
                        metadata = reader.metadata
                        metadata_str = str(metadata)
                        self.metadata = metadata_str
                    
                        logging.info(f"Metadata read for file: {file_path}")
                        
                        
                        for key, value in metadata.items():
                            if key == "/Title":
                                logging.info(f"Title: {value}")
                            if key == "/Author":
                                logging.info(f"Author: {value}")
                            if key == "/CreationDate":
                                logging.info(f"Creation date: {value}")
                    else:
                        logging.warning(f"File not found: {file_path}")
        

# Main Process for execution
async def main(*args, **kwargs):
    await pdfClient.write_metadata()
    await pdfClient.read_metadata()
    

if __name__ == "__main__":
    # Run the main process
    asyncio.run(main())
    print("Check the logs for more details")