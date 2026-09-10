import uuid,datetime,sqlite3
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_PATH = BASE_DIR / "DATABASE_PATH"
app = FastAPI()

ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]
MAX_FILE_SIZE = 10 * 1024* 1024

# SQLite connection
try:
    connection = sqlite3.connect('DATABASE_PATH')
    cursor = connection.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS documents(
    document_id TEXT PRIMARY KEY NOT NULL,
    original_filename TEXT,
    stored_filename TEXT,
    mime_type TEXT,
    file_size INT,
    status TEXT,
    uploaded_at TEXT)
    '''
    cursor.execute(query)
    print('Table created successfully')
    connection.close()

except Exception as e:
    print("Something went wrong upon initializing database")
    print(e)

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
    unique_filename = f"{unique_id}_{filename}"
    print(unique_id,unique_filename)
    file_path = UPLOAD_DIR/unique_filename
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
                                stored_filename=unique_filename,
                                mime_type=file_type,
                                file_size=file_size,
                                status='uploaded',
                                uploaded_at=str(timestamp))
    # Inserting data to database
    connection = sqlite3.connect('DATABASE_PATH')
    cursor = connection.cursor()
    print(metaobject)
    query = """
INSERT INTO documents (
    document_id,
    original_filename,
    stored_filename,
    mime_type,
    file_size,
    status,
    uploaded_at
)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""
   
    cursor.execute(query,
                   (
        metaobject.document_id,
        metaobject.original_filename,
        metaobject.stored_filename,
        metaobject.mime_type,
        metaobject.file_size,
        metaobject.status,
        metaobject.uploaded_at
    ))
    connection.commit()
    print('Inserted data successfully')
    return metaobject

@app.get('/documents/{document_id}')
async def display_document_metaobject(document_id: str):

    connection = sqlite3.connect('DATABASE_PATH')
    cursor = connection.cursor()
    query = """
    SELECT * FROM documents
    WHERE document_id = ?
    """
    cursor.execute(query, (document_id,))
    result = cursor.fetchone()
    connection.close()
    if not result:
        raise HTTPException(status_code=404,detail='id not found')
    return FileMetaObject(
    document_id=result[0],
    original_filename=result[1],
    stored_filename=result[2],
    mime_type=result[3],
    file_size=result[4],
    status=result[5],
    uploaded_at=result[6]
)

@app.get('/documents')
async def get_all_documents():
    connection = sqlite3.connect('metadata.db')
    cursor = connection.cursor()
    list_of_metaobjects = []
    query = '''
    SELECT * FROM documents
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()
    for row in rows:
        metaobject = FileMetaObject(document_id=row[0],
                                    original_filename=row[1],
                                    stored_filename=row[2],
                                    mime_type=row[3],
                                    file_size=row[4],
                                    status=row[5],
                                    uploaded_at=row[6])
        list_of_metaobjects.append(metaobject)
    
    return list_of_metaobjects

   
    
    