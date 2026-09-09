import uuid,datetime,json
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
documents = {}

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
    
    unique_id = str(uuid.uuid4())
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
    metaobject = FileMetaObject(document_id=unique_id,
                                original_filename=filename,
                                stored_filename=unique_file_name,
                                mime_type=file_type,
                                file_size=file_size,
                                status='uploaded',
                                uploaded_at=str(timestamp))
    documents[unique_id]= metaobject
    return metaobject

@app.get('/documents/{document_id}')
async def display_document_metaobject(document_id):
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status_code=404,detail='File not found')
    return document