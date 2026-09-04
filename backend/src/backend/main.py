from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import os
app = FastAPI()

class Item(BaseModel):
    name:str
    size:str
@app.get('/')
def home():
    return {'body':'Document processing API'}


@app.post("/upload")
async def upload_document(myfile: UploadFile = File(...)):

    print(f"Name of file is {myfile.filename}")
    print(f"Content type is {myfile.content_type}")

    content = await myfile.read()
    content = content.decode("utf-8")
    print(os.getcwd())
    try:
        with open(f"backend/uploads/{myfile.filename}", "a+") as file:
            file.write(content)

        return {
            "message": "Document is saved",
            "filename": myfile.filename
        }

    except Exception as e:
        print(e)
        return {
            "response": 500,
            "message": "Not saved"
        }