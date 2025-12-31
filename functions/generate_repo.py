import os
import asyncio
import shutil
import subprocess
from PyPDF2 import PdfReader


class SimpleGitHandler:
    def __init__(self):
        self.U_HOME = os.getenv("HOME")
        self.repo_url = "https://github.com/kid-gorgeous/books.git"

    @classmethod
    async def clone_repo(self, repo_url):
        process = await asyncio.create_subprocess_exec(
            "git", "clone", repo_url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        print(stdout.decode())
        if stderr:
            print(stderr.decode())

    def run(self) -> bool:
        asyncio.run(self.clone_repo(self.repo_url))


class RepoClient(SimpleGitHandler):
    def __init__(self):
        super().__init__()
        self.folder_path = f"{self.U_HOME}/Documents/home/knowledgebase/books/books"


    @staticmethod
    def folderSize(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size * 1e-6 # megabytes 233 MBs
    

    


if __name__ == "__main__":
    repo = RepoClient()
    print(repo.folderSize())