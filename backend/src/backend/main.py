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

@app.post('/upload')
async def upload_document(myfile: UploadFile = File(...)):
    print(f'Name of file is {myfile.content_type}')
    # file = open(myfile,'r')
    # content = file.read()
    # print(content)
    # file.close()
   
    return {'message':'Document is saved'}