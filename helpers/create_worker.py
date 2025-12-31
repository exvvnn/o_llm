
import os
import sys
import time

from multiprocessing import Process, Queue
from pydantic import BaseModel

# Version 2 
class Task(BaseModel):
    task: str
    task_id: int


# Version 1 
class Worker:

    def __init__(self):
        self.task_queue = Queue()
        
    def add_task(self, task):
        self.task_queue.put(task)

    def run(self):
        task_queue = self.task_queue
        while not task_queue.empty():
            task = task_queue.get()
            print(f"Task: {task}")
            time.sleep(1)


