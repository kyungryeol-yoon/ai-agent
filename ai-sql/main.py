from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# 1. Embedding 모델 설정 (Ollama 사용)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. 예시 데이터 (문서화)
docs = [
    Document(page_content="LangChain은 LLM 애플리케이션을 개발하기 위한 프레임워크입니다."),
    Document(page_content="LangGraph는 순환 그래프를 통해 상태 보존형 에이전트를 구축하게 해줍니다."),
    Document(page_content="Vector DB는 고차원 벡터 데이터를 저장하고 검색하는 데 최적화되어 있습니다.")
]

# 3. Vector DB 생성 및 저장 (로컬 Chroma DB)
vectorstore = Chroma.from_documents(
    documents=docs, 
    embedding=embeddings,
    collection_name="local-rag"
)

print("Vector DB 구축 완료!")