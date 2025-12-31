from multiprocessing import Pool, TimeoutError
import time
import os
import asyncio
from PyPDF2 import PdfReader

from functions.generate_pdf_batches import PDFClient



def get_book_metadata():
    pdfClient = PDFClient()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(pdfClient.read_metadata())
    

def get_booktext():
    pdfClient = PDFClient()
    loop = asyncio.get_event_loop()
    book_list = []
    start = time.time()
    for root, dirs, files in os.walk(pdfClient.datalake_path):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                
                if os.path.exists(file_path):
                    reader = PdfReader(file_path)
                    book_text = ""
                    for page in reader.pages:
                        book_text += page.extract_text()
                    book_list.append(book_text)
                else:
                    print(f"File not found: {file_path}")
    end = time.time()
                
    return loop.run_until_complete(pdfClient.get_booktext())


import sqlite3


def create_sql_table():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE books
                 (name text, author text, year text)''')
    conn.commit()
    conn.close()
    



if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description='Create a process pool and thread executor for a sql database.')
    parser.add_argument('--processes', type=int, default=4, help='Number of processes to create in the pool')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to create in the executor')
    
    # Add more arguments as needed
    parser.add_argument('--create_sql', action='store_true', help='Create SQL table')
    
    def print(p):
        return f"hello from process {p}"
    
    args = parser.parse_args()
    if args.create_sql:
        create_sql_table()

    if args.processes > 0:

        process = args.processes

        with Pool(args.processes) as pool:
            # Use the pool to run get_book_metadata in parallel
            results = pool.apply_async(print(process))
            print(results.get(timeout=10))


    
