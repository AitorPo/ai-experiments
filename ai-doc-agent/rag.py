from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.llms.ollama import Ollama


def run_rag(query, embeddings):
    #faiss.read_index("index.faiss")
    try:
        retriever = FAISS.load_local("ai-doc-agent", embeddings=embeddings, allow_dangerous_deserialization=True)
    except Exception:
        retriever = FAISS.load_local(".", embeddings=embeddings, allow_dangerous_deserialization=True)

    llm = Ollama(model="mistral")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever.as_retriever(), return_source_documents=True)
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