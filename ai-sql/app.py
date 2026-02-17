import streamlit as st
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. 페이지 설정 및 레이아웃
st.set_page_config(page_title="Local SQL/API Agent", layout="wide")
st.title("🤖 Local SQL & Swagger Assistant")
st.markdown("""
이 시스템은 **BGE-M3** 모델을 통해 기술 문서를 수치화하고, 
**Ollama(Llama3)**를 통해 로컬 환경에서 안전하게 답변을 생성합니다.
""")

# 2. 모델 및 DB 로드 (캐싱 처리하여 속도 최적화)
@st.cache_resource
def initialize_system():
    # 임베딩 모델 로드 (BGE-M3)
    # 수치화 원리: 텍스트를 1024차원의 벡터로 변환 (코사인 유사도 기반 검색)
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 예시 데이터 (실제 프로젝트에서는 파일 로더를 통해 확장 가능)
    raw_data = [
        {"content": "SELECT * FROM orders WHERE status = 'PENDING';", "desc": "대기 중인 주문을 조회하는 SQL입니다."},
        {"content": "POST /api/v1/login", "desc": "사용자 로그인을 위한 Swagger API 명세입니다. ID/PW가 필요합니다."},
        {"content": "CREATE TABLE users (id INT, name TEXT);", "desc": "사용자 테이블을 생성하는 DDL 문입니다."}
    ]
    docs = [Document(page_content=f"{d['content']}\n설명: {d['desc']}") for d in raw_data]
    
    # Vector DB 구축 (로컬 저장소: ./chroma_db)
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=embeddings, 
        persist_directory="./chroma_db"
    )
    
    # LLM 설정 (Ollama)
    llm = OllamaLLM(model="llama3")
    
    return vectorstore.as_retriever(search_kwargs={"k": 2}), llm

retriever, llm = initialize_system()

# 3. RAG 체인 구성 (LangChain)
template = """당신은 IT 기술 문서 전문가입니다. 아래 제공된 문맥(Context)을 사용하여 질문에 답하세요.
모르는 내용이라면 억지로 만들지 말고 모른다고 답하세요.

[Context]
{context}

[Question]
{question}

답변은 항상 한국어로 친절하게 작성해 주세요.
"""
prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 4. 채팅 UI 구현
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력창
if user_input := st.chat_input("질문을 입력하세요 (예: 로그인 API 정보 알려줘)"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("로컬 지식 베이스(Vector DB) 검색 중..."):
            response = rag_chain.invoke(user_input)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})