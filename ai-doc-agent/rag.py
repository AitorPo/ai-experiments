from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.llms.ollama import Ollama
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
import pickle
import os

def run_rag_with_vectorstore(query, vectorstore, embeddings=None):
    """
    Run RAG query using an existing vectorstore object
    """
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
        
        llm = Ollama(model="mistral")
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
        result = qa.invoke({"query": query})
        answer = result["result"]
        sources = result["source_documents"]
        print("\nAnswer:")
        print(answer)
        print("\nSources:")
        for doc in sources:
            meta = doc.metadata
            print(f"- File: {meta.get('file', 'N/A')} | Page: {meta.get('page', 'N/A')}")

        return answer
        
    except Exception as e:
        print(f"Error running RAG with vectorstore: {e}")
        return None

def run_rag(query, embeddings, vectorstore=None):
    """
    Run RAG query. If vectorstore is provided, use it directly.
    Otherwise, load from files as before.
    """
    if vectorstore is not None:
        return run_rag_with_vectorstore(query, vectorstore, embeddings)
    
    try:
        # Load index and metadata using the same approach as add_to_index.py
        index_path = "index.faiss"
        pkl_path = "index.pkl"
        
        # Check if files exist in current directory or ai-doc-agent subdirectory
        if not os.path.exists(index_path):
            index_path = "ai-doc-agent/index.faiss"
            pkl_path = "ai-doc-agent/index.pkl"
        
        if not os.path.exists(index_path):
            print("Index files not found. Please create an index first.")
            return None
        
        # Load index and metadata
        index = faiss.read_index(index_path)
        with open(pkl_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Create docstore
        docstore = InMemoryDocstore(metadata['docstore_docs'])
        
        # Create vectorstore
        vectorstore = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=docstore,
            index_to_docstore_id=metadata['index_to_docstore_id']
        )
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        
    except Exception as e:
        print(f"Error loading index: {e}")
        return None

    llm = Ollama(model="mistral")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    result = qa.invoke({"query": query})
    answer = result["result"]
    sources = result["source_documents"]
    print("\nAnswer:")
    print(answer)
    print("\nSources:")
    for doc in sources:
        meta = doc.metadata
        print(f"- File: {meta.get('file', 'N/A')} | Page: {meta.get('page', 'N/A')}")

    return answer