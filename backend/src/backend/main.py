import uuid
import datetime
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()

ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]
MAX_FILE_SIZE = 10 * 1024* 1024
"""
UUID              → document ID
Original filename → filename
Stored filename   → UUID + filename
MIME type         → content_type
File size         → size validation logic
Status            → uploaded
"""
class FileMetaObject(BaseModel):
    document_id:str
    original_filename:str
    stored_filename:str
    mime_type:str
    file_size:int
    status:str
    uploaded_at: str

@app.get("/")
async def main():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="file" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post('/uploadfiles')
async def test_upload_doc_type(file: UploadFile = File(...)):
    filename = file.filename
    filetype = file.content_type
    return {
        'status':'saved','file_type':filetype
    }

@app.post("/upload")
async def upload_document(myfile: UploadFile = File(...)):

    filename = Path(myfile.filename).name
    file_type = myfile.content_type

    # File type validation
    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=415,detail="Unsupported file extension",)
    
    # Size validation
    myfile.file.seek(0)
    myfile.file.seek(0,2)
    file_size = myfile.file.tell()
    myfile.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413,detail='File content is too large')

    content = await myfile.read()
    
    unique_id = uuid.uuid4()
    unique_file_name = f"{unique_id}_{filename}"
    print(unique_id,unique_file_name)
    file_path = UPLOAD_DIR/unique_file_name
    timestamp = datetime.datetime.now()
    try:
        with open(file_path, "wb") as file:
            file.write(content)
        
    except Exception as e:
        print(e)
        return {
            "response": 500,
            "message": "Not saved"
        }
    metaobject = FileMetaObject(document_id=str(unique_id),
                                original_filename=filename,
                                stored_filename=unique_file_name,
                                mime_type=file_type,
                                file_size=file_size,
                                status='uploaded',
                                uploaded_at=str(timestamp))
    return metaobject

def validate_file_type(file):
    if file in ALLOWED_FILE_TYPES:
        return True
    else:
        return False