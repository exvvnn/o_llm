import hashlib
import json
import uuid
import os 


from pydantic import BaseModel

class Prompt(BaseModel):
    filename: str
    system: str
    user: str
    role: str
    content: str


def createPrompt(filename, system, user, role, content):
    data = {
        "system": system,
        "user": user,
        "role": role,
        "content": content, 
    }
    return data


def saveJSON(filepath, filename, data):
    with open(f"{filepath}/{filename}.json", "w") as file:
        json.dump(data, file)
    print("JSON saved")


if __name__ == "__main__":
    filepath = "./vaults/.prompts"
    
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    prompt = createPrompt("File1", "macOS", "user", "system", "new data")
    saveJSON(filepath, "prompt1", prompt)

