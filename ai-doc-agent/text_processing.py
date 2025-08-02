import pymupdf
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

def extract_text(file_path):
    doc = pymupdf.open(file_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "file": file_path,
            "page": i + 1,
            "text": text
        })
    return pages

def chunk_text(text, size=500, overlap=100):
    """
    Chunk text into smaller chunks of a given size with an overlap.
    Overlap helps to avoid losing information when the chunks are joined 
    ensuring that context doesn't break between chunks.
    It's essential for coherent answers.
    """
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunk = text[i:i + size]
        chunks.append(chunk)
    return chunks

model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
def embed_chunks(chunks):
    """
    Embed chunks using the SentenceTransformer model.
    """
    return model.embed_documents(chunks)