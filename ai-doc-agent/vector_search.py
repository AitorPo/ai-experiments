import faiss
import numpy as np
import pickle

def build_index(embeddings):
    embeddings_np = np.array(embeddings).astype("float32")  # FAISS requires float32
    dim = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)
    return index

def save_index(index, path):
    faiss.write_index(index, path)

def load_index(path):
    return faiss.read_index(path)

def save_metadata(index_to_docstore_id, docstore, path):
    with open(path, "wb") as f:
        pickle.dump((index_to_docstore_id, docstore), f)

def load_metadata(path):
    with open(path, "rb") as f:
        return pickle.load(f)