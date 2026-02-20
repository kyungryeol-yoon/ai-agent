import requests
import os
import shutil
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

def sync_swagger(url, embeddings):
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
    
    response = requests.get(url, timeout=10, verify=False)
    response.raise_for_status()
    data = response.json()
    docs = []
    
    for path, methods in data.get("paths", {}).items():
        for method, details in methods.items():
            summary = details.get("summary", "").strip()
            if not summary: continue # Summary 없으면 패스
            
            content = f"Endpoint: {method.upper()} {path}\nSummary: {summary}\nParams: {details.get('parameters', '')}"
            docs.append(Document(page_content=content, metadata={"path": path, "method": method}))
    
    if docs:
        Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory="./chroma_db")
        return len(docs)
    return 0