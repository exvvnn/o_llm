import os
import ast
from pydantic import BaseModel
from typing import List


class Book(BaseModel):
    Title: str
    Author: str
    CreationDate: str
    Publisher: str


class Catalog:
    def __init__(self):
        self.catalog: List[Book] = []
        self.user_dir = os.getenv("HOME")

        # Define the path to the metadata file - TODO: replace with env var
        self.metadata_file = os.path.join(self.user_dir, "Documents/home/knowledgebase/data/folder_metadata.txt")

    def load_book_metadata(self):
        """Load books from the metadata file."""
        if not os.path.exists(self.metadata_file):
            print(f"Metadata file not found: {self.metadata_file}")
            return

        with open(self.metadata_file, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    # Parse the metadata string into a dictionary
                    metadata = ast.literal_eval(line.strip())
                    # Create a Book instance from the metadata
                    book = Book(
                        Title=metadata.get("/Title", "Unknown Title"),
                        Author=metadata.get("/Author", "Unknown Author"),
                        CreationDate=metadata.get("/CreationDate", "Unknown Date"),
                        Publisher=metadata.get("/EBX_PUBLISHER", "Unknown Publisher"),
                    )
                    self.catalog.append(book)
                except Exception as e:
                    print(f"Error parsing line: {line.strip()}\n{e}")

    def __str__(self):
        """String representation of the catalog."""
        return "\n".join([f"{book.Title} by {book.Author} ({book.CreationDate})" for book in self.catalog])


if __name__ == "__main__":
    catalog = Catalog()
    catalog.load_book_metadata()
    print(catalog)