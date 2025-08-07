import os
from text_processing import extract_text, embed_chunks, model
from vector_search import build_index, save_index, load_index, save_metadata, load_metadata
from langchain.schema import Document
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

import numpy as np
import faiss
import pickle

def load_existing_index(index_path="index.faiss", pkl_path="index.pkl"):
    """
    Load existing FAISS index and metadata from files
    """
    try:
        # Load existing index
        index = faiss.read_index(index_path)
        
        # Load existing metadata
        with open(pkl_path, 'rb') as f:
            metadata = pickle.load(f)
            
        return index, metadata
    except (FileNotFoundError, RuntimeError):
        print(f"Index files not found. Creating new index.")
        return None, None

def add_document_to_index(file_path, embedding_model, index_path="index.faiss", pkl_path="index.pkl"):
    """
    Add a new document to the existing index and save updated files
    """
    # Load existing index and metadata
    existing_index, existing_metadata = load_existing_index(index_path, pkl_path)
    
    # Extract text from new document
    pages = extract_text(file_path)
    documents = []
    
    # Prepare documents from new file
    for i, page in enumerate(pages):
        doc = Document(
            page_content=page["text"],
            metadata={"file": page['file'], "page": page["page"]}
        )
        documents.append(doc)
    
    # Embed new documents
    raw_texts = [doc.page_content for doc in documents]
    embeddings = embed_chunks(raw_texts)
    embeddings_np = np.array(embeddings).astype("float32")
    
    if existing_index is None:
        # Create new index if none exists
        dim = embeddings_np.shape[1]
        index = faiss.IndexFlatL2(dim)
        docstore_docs = {}
        index_to_docstore_id = {}
        
        # Add new documents to index
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = f"{file_path}_page_{i}"
            docstore_docs[doc_id] = doc
            index_to_docstore_id[i] = doc_id
        
        index.add(embeddings_np)
        
        # Create metadata
        metadata = {
            'docstore_docs': docstore_docs,
            'index_to_docstore_id': index_to_docstore_id
        }
        
    else:
        # Add to existing index
        current_size = existing_index.ntotal
        
        # Update existing metadata
        docstore_docs = existing_metadata['docstore_docs'].copy()
        index_to_docstore_id = existing_metadata['index_to_docstore_id'].copy()
        
        # Add new documents
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = f"{file_path}_page_{i}"
            docstore_docs[doc_id] = doc
            index_to_docstore_id[current_size + i] = doc_id
        
        # Add embeddings to existing index
        existing_index.add(embeddings_np)
        index = existing_index
        
        # Update metadata
        metadata = {
            'docstore_docs': docstore_docs,
            'index_to_docstore_id': index_to_docstore_id
        }
    
    # Save updated index and metadata
    faiss.write_index(index, index_path)
    with open(pkl_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"Successfully added {len(documents)} pages from {file_path} to index")
    print(f"Total documents in index: {index.ntotal}")
    
    return index, metadata

def create_vectorstore_from_files(index_path="index.faiss", pkl_path="index.pkl"):
    """
    Create a FAISS vectorstore object from saved index and metadata files
    """
    try:
        # Load index and metadata
        index = faiss.read_index(index_path)
        with open(pkl_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Create docstore
        docstore = InMemoryDocstore(metadata['docstore_docs'])
        
        # Create vectorstore
        vectorstore = FAISS(
            embedding_function=model.embed_query,
            index=index,
            docstore=docstore,
            index_to_docstore_id=metadata['index_to_docstore_id']
        )
        
        return vectorstore
        
    except (FileNotFoundError, RuntimeError):
        print("Index files not found. Please create an index first.")
        return None

def add_multiple_files(file_paths, embedding_model, index_path="index.faiss", pkl_path="index.pkl"):
    """
    Add multiple files to the index at once
    """
    for file_path in file_paths:
        if os.path.exists(file_path):
            print(f"Processing {file_path}...")
            add_document_to_index(file_path, embedding_model, index_path, pkl_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    # Example usage: Add a new document to existing index
    new_file_path = f"{os.getcwd()}/ai-doc-agent/new_document.pdf"  # Replace with your new file
    
    # Add single file
    if os.path.exists(new_file_path):
        add_document_to_index(new_file_path, model)
    else:
        print(f"File not found: {new_file_path}")
        print("Please provide a valid file path to add to the index")
    
    # Example: Add multiple files
    # multiple_files = [
    #     f"{os.getcwd()}/ai-doc-agent/doc1.pdf",
    #     f"{os.getcwd()}/ai-doc-agent/doc2.pdf",
    #     f"{os.getcwd()}/ai-doc-agent/doc3.pdf"
    # ]
    # add_multiple_files(multiple_files, model) 