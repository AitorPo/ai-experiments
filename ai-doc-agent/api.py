import os

import uvicorn
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from rag import run_rag
from text_processing import model
from main import process_file

class Query(BaseModel):
    question: str
app = FastAPI()

@app.post("/ask")
def ask(query: Query):
    response = run_rag(query.question, model)
    return {"answer": response}

@app.post("/upload")
async def upload_pdf(file: UploadFile):
    os.makedirs('./docs', exist_ok=True)
    save_path = f"./docs/{file.filename}"
    with open(save_path, "wb") as f:
        f.write(await file.read())
    process_file(save_path, model)
    # Extract, chunk, embed, and update FAISS index.
    return {"message": "PDF uploaded successfully"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
