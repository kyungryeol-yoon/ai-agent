import requests
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

def sync_swagger(url, embeddings):
    try:
        response = requests.get(url)
        data = response.json()
        docs = []
        for path, methods in data.get("paths", {}).items():
            for method, details in methods.items():
                content = f"API: {method.upper()} {path}\n요약: {details.get('summary', '')}\n설명: {details.get('description', '')}"
                docs.append(Document(page_content=content, metadata={"source": url}))
        
        Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory="./chroma_db")
        return len(docs)
    except Exception as e:
        raise e