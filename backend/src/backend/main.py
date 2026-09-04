from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
UPLOAD_DIR = Path('backend/uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()


@app.get('/')
def home():
    return {'body':'Document processing API'}


@app.post("/upload")
async def upload_document(myfile: UploadFile = File(...)):

    filename = myfile.filename
    file_type = myfile.content_type

    content = await myfile.read()
    
    # print(os.getcwd())
    file_path = UPLOAD_DIR/filename
    try:
        with open(file_path, "wb") as file:
            file.write(content)

        return {
            "message": "Document is saved",
            "filename": filename,
            "file_type": file_type
        }

    except Exception as e:
        print(e)
        return {
            "response": 500,
            "message": "Not saved"
        }