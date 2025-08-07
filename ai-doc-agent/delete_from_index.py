import os
import faiss
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
from langchain.schema import Document
from text_processing import embed_chunks

def load_existing_index(index_path="index.faiss", pkl_path="index.pkl"):
    """
    Load existing FAISS index and metadata from files
    """
    try:
        # Check if files exist in current directory or ai-doc-agent subdirectory
        if not os.path.exists(index_path):
            index_path = "ai-doc-agent/index.faiss"
            pkl_path = "ai-doc-agent/index.pkl"
        
        if not os.path.exists(index_path):
            print("Index files not found.")
            return None, None
        
        # Load existing index
        index = faiss.read_index(index_path)
        
        # Load existing metadata
        with open(pkl_path, 'rb') as f:
            metadata = pickle.load(f)
            
        return index, metadata
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error loading index: {e}")
        return None, None

def save_index_and_metadata(index, metadata, index_path="index.faiss", pkl_path="index.pkl"):
    """
    Save FAISS index and metadata to files
    """
    try:
        # Check if files exist in current directory or ai-doc-agent subdirectory
        if not os.path.exists(index_path):
            index_path = "ai-doc-agent/index.faiss"
            pkl_path = "ai-doc-agent/index.pkl"
        
        faiss.write_index(index, index_path)
        with open(pkl_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Successfully saved updated index and metadata")
        return True
    except Exception as e:
        print(f"Error saving index: {e}")
        return False

def delete_document_by_filename(filename: str, index_path="index.faiss", pkl_path="index.pkl") -> bool:
    """
    Delete all pages from a specific document by filename
    """
    index, metadata = load_existing_index(index_path, pkl_path)
    if index is None or metadata is None:
        return False
    
    # Find all document IDs that match the filename
    docstore_docs = metadata['docstore_docs']
    index_to_docstore_id = metadata['index_to_docstore_id']
    
    # Find indices to remove
    indices_to_remove = []
    for idx, doc_id in index_to_docstore_id.items():
        if doc_id.startswith(filename):
            indices_to_remove.append(idx)
    
    if not indices_to_remove:
        print(f"No documents found with filename: {filename}")
        return False
    
    return _remove_indices_from_index(index, metadata, indices_to_remove, index_path, pkl_path)

def delete_document_by_page(filename: str, page_number: int, index_path="index.faiss", pkl_path="index.pkl") -> bool:
    """
    Delete a specific page from a document
    """
    index, metadata = load_existing_index(index_path, pkl_path)
    if index is None or metadata is None:
        return False
    
    # Find the specific document ID for this page
    target_doc_id = f"{filename}_page_{page_number - 1}"  # page_number is 1-indexed, but our IDs are 0-indexed
    
    index_to_docstore_id = metadata['index_to_docstore_id']
    
    # Find the index to remove
    index_to_remove = None
    for idx, doc_id in index_to_docstore_id.items():
        if doc_id == target_doc_id:
            index_to_remove = idx
            break
    
    if index_to_remove is None:
        print(f"Page {page_number} not found in document: {filename}")
        return False
    
    return _remove_indices_from_index(index, metadata, [index_to_remove], index_path, pkl_path)

def delete_documents_by_content(content_query: str, index_path="index.faiss", pkl_path="index.pkl") -> bool:
    """
    Delete documents that contain specific content (case-insensitive search)
    """
    index, metadata = load_existing_index(index_path, pkl_path)
    if index is None or metadata is None:
        return False
    
    docstore_docs = metadata['docstore_docs']
    index_to_docstore_id = metadata['index_to_docstore_id']
    
    # Find indices to remove based on content
    indices_to_remove = []
    content_query_lower = content_query.lower()
    
    for idx, doc_id in index_to_docstore_id.items():
        doc = docstore_docs.get(doc_id)
        if doc and content_query_lower in doc.page_content.lower():
            indices_to_remove.append(idx)
    
    if not indices_to_remove:
        print(f"No documents found containing: {content_query}")
        return False
    
    return _remove_indices_from_index(index, metadata, indices_to_remove, index_path, pkl_path)

def list_documents_in_index(index_path="index.faiss", pkl_path="index.pkl") -> Dict[str, List[int]]:
    """
    List all documents and their pages in the index
    """
    index, metadata = load_existing_index(index_path, pkl_path)
    if index is None or metadata is None:
        return {}
    
    docstore_docs = metadata['docstore_docs']
    index_to_docstore_id = metadata['index_to_docstore_id']
    
    documents = {}
    for idx, doc_id in index_to_docstore_id.items():
        doc = docstore_docs.get(doc_id)
        if doc:
            filename = doc.metadata.get('file', 'Unknown')
            page = doc.metadata.get('page', 0)
            
            if filename not in documents:
                documents[filename] = []
            documents[filename].append(page)
    
    return documents

def get_index_statistics(index_path="index.faiss", pkl_path="index.pkl") -> Dict:
    """
    Get statistics about the current index
    """
    index, metadata = load_existing_index(index_path, pkl_path)
    if index is None or metadata is None:
        return {}
    
    docstore_docs = metadata['docstore_docs']
    index_to_docstore_id = metadata['index_to_docstore_id']
    
    # Count documents by filename
    documents = list_documents_in_index(index_path, pkl_path)
    total_pages = sum(len(pages) for pages in documents.values())
    
    return {
        'total_documents': len(documents),
        'total_pages': total_pages,
        'index_size': index.ntotal,
        'documents': documents
    }

def _remove_indices_from_index(index, metadata, indices_to_remove: List[int], index_path: str, pkl_path: str) -> bool:
    """
    Internal function to remove specific indices from the FAISS index and update metadata
    """
    try:
        # Sort indices in descending order to avoid index shifting issues
        indices_to_remove = sorted(indices_to_remove, reverse=True)
        
        # Create new index with same dimension
        # We'll need to get the dimension from the existing index
        # For now, we'll use the default dimension (384 for all-MiniLM-L6-v2)
        dim = 384
        new_index = faiss.IndexFlatL2(dim)
        
        # Prepare new metadata
        new_docstore_docs = {}
        new_index_to_docstore_id = {}
        
        # Rebuild index and metadata excluding removed indices
        # We need to re-embed the remaining documents since we can't reconstruct vectors from FAISS
        remaining_docs = []
        new_idx = 0
        for old_idx in range(index.ntotal):
            if old_idx not in indices_to_remove:
                # Get the document
                doc_id = metadata['index_to_docstore_id'][old_idx]
                doc = metadata['docstore_docs'][doc_id]
                
                # Add to remaining docs for re-embedding
                remaining_docs.append(doc)
                
                # Update metadata
                new_docstore_docs[doc_id] = doc
                new_index_to_docstore_id[new_idx] = doc_id
                new_idx += 1
        
        # Re-embed remaining documents
        if remaining_docs:
            raw_texts = [doc.page_content for doc in remaining_docs]
            embeddings = embed_chunks(raw_texts)
            embeddings_np = np.array(embeddings).astype("float32")
            new_index.add(embeddings_np)
        
        # Create new metadata
        new_metadata = {
            'docstore_docs': new_docstore_docs,
            'index_to_docstore_id': new_index_to_docstore_id
        }
        
        # Save updated index and metadata
        success = save_index_and_metadata(new_index, new_metadata, index_path, pkl_path)
        
        if success:
            print(f"Successfully removed {len(indices_to_remove)} documents from index")
            print(f"New index size: {new_index.ntotal}")
        
        return success
        
    except Exception as e:
        print(f"Error removing indices from index: {e}")
        return False

def delete_all_documents(index_path="index.faiss", pkl_path="index.pkl") -> bool:
    """
    Delete all documents from the index (creates empty index)
    """
    try:
        # Check if files exist in current directory or ai-doc-agent subdirectory
        if not os.path.exists(index_path):
            index_path = "ai-doc-agent/index.faiss"
            pkl_path = "ai-doc-agent/index.pkl"
        
        # Create empty index with default dimension (384 for all-MiniLM-L6-v2)
        dim = 384
        new_index = faiss.IndexFlatL2(dim)
        
        # Create empty metadata
        new_metadata = {
            'docstore_docs': {},
            'index_to_docstore_id': {}
        }
        
        # Save empty index and metadata
        success = save_index_and_metadata(new_index, new_metadata, index_path, pkl_path)
        
        if success:
            print("Successfully cleared all documents from index")
        
        return success
        
    except Exception as e:
        print(f"Error clearing index: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    print("Document deletion utility")
    print("=" * 50)
    
    # Show current index statistics
    stats = get_index_statistics()
    if stats:
        print(f"Current index statistics:")
        print(f"- Total documents: {stats['total_documents']}")
        print(f"- Total pages: {stats['total_pages']}")
        print(f"- Index size: {stats['index_size']}")
        print("\nDocuments in index:")
        for filename, pages in stats['documents'].items():
            print(f"  {filename}: {len(pages)} pages")
    else:
        print("No index found or error loading index")
    
    print("\nAvailable operations:")
    print("1. delete_document_by_filename('filename.pdf')")
    print("2. delete_document_by_page('filename.pdf', page_number)")
    print("3. delete_documents_by_content('search term')")
    print("4. delete_all_documents()")
    print("5. list_documents_in_index()")
    print("6. get_index_statistics()")
