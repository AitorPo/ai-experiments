import os

import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from rag import run_rag
from text_processing import model
from add_to_index import add_document_to_index
from delete_from_index import (
    delete_document_by_filename,
    delete_document_by_page,
    delete_documents_by_content,
    delete_all_documents,
    list_documents_in_index,
    get_index_statistics
)

class Query(BaseModel):
    question: str

class DeleteDocumentRequest(BaseModel):
    filename: str

class DeletePageRequest(BaseModel):
    filename: str
    page_number: int

class DeleteContentRequest(BaseModel):
    content_query: str

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
    add_document_to_index(save_path, model)
    # Extract, chunk, embed, and update FAISS index.
    return {"message": "PDF uploaded successfully"}

@app.delete("/documents")
async def delete_document(request: DeleteDocumentRequest):
    """Delete all pages from a specific document"""
    success = delete_document_by_filename(request.filename)
    if success:
        return {"message": f"Successfully deleted document: {request.filename}"}
    else:
        raise HTTPException(status_code=404, detail=f"Document not found: {request.filename}")

@app.delete("/documents/page")
async def delete_page(request: DeletePageRequest):
    """Delete a specific page from a document"""
    success = delete_document_by_page(request.filename, request.page_number)
    if success:
        return {"message": f"Successfully deleted page {request.page_number} from {request.filename}"}
    else:
        raise HTTPException(status_code=404, detail=f"Page not found: {request.filename} page {request.page_number}")

@app.delete("/documents/content")
async def delete_by_content(request: DeleteContentRequest):
    """Delete documents containing specific content"""
    success = delete_documents_by_content(request.content_query)
    if success:
        return {"message": f"Successfully deleted documents containing: {request.content_query}"}
    else:
        raise HTTPException(status_code=404, detail=f"No documents found containing: {request.content_query}")

@app.delete("/documents/all")
async def delete_all_docs():
    """Delete all documents from the index"""
    success = delete_all_documents()
    if success:
        return {"message": "Successfully cleared all documents from index"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear index")

@app.get("/documents")
async def list_docs():
    """List all documents in the index"""
    documents = list_documents_in_index()
    return {"documents": documents}

@app.get("/documents/stats")
async def get_stats():
    """Get statistics about the current index"""
    stats = get_index_statistics()
    return stats

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
