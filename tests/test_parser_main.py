import os
import sys
import asyncio
import datetime
from argparse import ArgumentParser

# Globals
arg = ArgumentParser()
U_HOME = os.getenv("HOME")
current_time = datetime.datetime.now()

# Args
arg.add_argument("clone", action="store_true", help="Clone git repo")
arg.add_argument("create_env", action="store_true", help="Create Objects")
arg.add_argument("read", action="store_true", help="Read Objects")
arg.add_argument("update", action="store_true", help="Update Objects")
arg.add_argument("--delete", action="store_true", help="Delete Objects")
arg.add_argument("--install", action="store_true", help="Install System")

# Libraries
# from functions.generate_excel_spreadsheet import ExcelClient
# from functions.generate_repo import RepoClient

# Clients


# Main function
if __name__ == "__main__":

    # xlsxClient = ExcelClient()
    args = arg.parse_args()

    if args.create_env:
        os.system("python3.11.16 -m venv .venv")
    if args.install:
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        os.system("fish -c 'source .venv/bin/activate.fish && pip3 install --upgrade pip && pip3 install -r requirements.txt --break-system-packages'")
        os.system("") # My dev install, sync and build manager
    if args.clone:
        from functions.generate_repo import SimpleGitClient
        if SimpleGitClient().run() is not None:
            print(f"Repo cloned successfully at: {current_time}")
        else:
            print(f"Repo not cloned: {current_time}")
    elif args.create:
        # xlsxClient.create_sheet("Sheet1", "DataTable")


    else:
        print("No repo to clone")

    
