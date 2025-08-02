import os
from text_processing import extract_text, embed_chunks, model
from rag import run_rag
from vector_search import build_index, save_index, load_index, save_metadata, load_metadata
from langchain.schema import Document

import numpy as np
import faiss
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.in_memory import InMemoryDocstore

def process_file(file_path, embedding_model):
    pages = extract_text(file_path)
    documents = []
    index_to_docstore_id = {}
    docstore_docs = {}

    for i, page in enumerate(pages):
        doc_id = f"{file_path}_page_{int(i)}"
        doc = Document(
            page_content=page["text"],
            metadata={"file": page['file'], "page": page["page"]}
        )
        documents.append(doc)
        index_to_docstore_id[int(i)] = doc_id
        docstore_docs[doc_id] = doc

    # Embed
    raw_texts = [doc.page_content for doc in documents]
    embeddings = embed_chunks(raw_texts)
    embeddings_np = np.array(embeddings).astype("float32")

    # Build FAISS index
    dim = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)

    # Wrap and save
    docstore = InMemoryDocstore(docstore_docs)
    vectorstore = FAISS(
        embedding_function=embedding_model.embed_query,  # or embedding_model.embed_documents
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    vectorstore.save_local(f"{os.getcwd()}/ai-doc-agent/")  # now load_local will work

    return vectorstore

if __name__ == "__main__":
    vectorstore = process_file(f"{os.getcwd()}/ai-doc-agent/test.pdf", model)
    #print(vectorstore)
    run_rag("Explain me, in a very detailed way, what is a C-FedRag", model)