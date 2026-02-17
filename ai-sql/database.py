import requests
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Swagger 문서를 가져와서 AI가 읽을 수 있는 형태로 가공
# requests로 JSON 데이터를 긁어옵니다.
# 복잡한 JSON 구조에서 paths(경로), methods(방식), summary(요약) 등을 추출하여 **하나의 기술 문서(Document)**로 만듭니다.
# Chroma DB에 저장합니다. 이때 persist_directory를 지정하여 프로그램이 꺼져도 지식이 사라지지 않게 합니다
def sync_swagger(url, embeddings):
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        docs = []
        
        paths = data.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                content = (
                    f"Endpoint: {method.upper()} {path}\n"
                    f"Summary: {details.get('summary', 'No summary')}\n"
                    f"Description: {details.get('description', 'No description')}\n"
                    f"Parameters: {details.get('parameters', [])}"
                )
                docs.append(Document(page_content=content, metadata={"source": url, "path": path}))
        
        # 데이터가 있을 경우에만 저장
        if docs:
            vectorstore = Chroma.from_documents(
                documents=docs, 
                embedding=embeddings, 
                persist_directory="./chroma_db"
            )
            return len(docs)
        return 0
    except Exception as e:
        raise Exception(f"동기화 중 오류 발생: {str(e)}")