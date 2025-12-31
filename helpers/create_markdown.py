

import os
import sys
import asyncio  
import datetime
import pandas as pd
from argparse import ArgumentParser

from pydantic import BaseModel
from typing import List, Optional


class ObsidianMarkdown(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
    def __str__(self):
        return f"Title: {self.title}, Tags: {self.tags}, Metadata: {self.metadata}"


class OBMarkdownHandler:
    def __init__(self):
        self.arg = ArgumentParser()
        self.U_HOME = os.getenv("HOME")
        self.current_time = datetime.datetime.now()

        self.arg.add_argument("clone", action="store_true", help="Clone git repo")
        self.arg.add_argument("create", action="store_true", help="Create Objects")
        self.arg.add_argument("read", action="store_true", help="Read Objects")
        self.arg.add_argument("update", action="store_true", help="Update Objects")
        self.arg.add_argument("delete", action="store_true", help="Delete Objects")
        

    
    async def OBMarkdownArgumentParser(self, args):
        # args = self.arg.parse_args()
        if args.clone:
            print("Cloning git repo...")
            # Add your cloning logic here
        if args.create:
            print("Creating objects...")
            # Add your object creation logic here
        if args.read:
            print("Reading objects...")
            # Add your object reading logic here
        if args.update:
            print("Updating objects...")
            # Add your object updating logic here
        if args.delete:
            print("Deleting objects...")
            # Add your object deletion logic here
        else:
            print("No valid argument provided. Use --help for more information.")



if __name__ == "__main__":
    
    obsidian_handler = OBMarkdownHandler()
    args = obsidian_handler.arg.parse_args() 
    asyncio.run(obsidian_handler.OBMarkdownArgumentParser(args))

    