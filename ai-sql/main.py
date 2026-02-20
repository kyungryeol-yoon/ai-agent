import streamlit as st
import os
from models import get_embeddings, get_llm_engine
from database import sync_swagger
from graph import create_retrieval_graph

# 환경변수 설정 (실제 환경에 맞게 수정)
os.environ["OPENAI_API_BASE"] = "https://your-internal-api/v1"
os.environ["OPENAI_API_KEY"] = "your-token"

st.title("🛡️ 사내 API 어시스턴트")

emb = get_embeddings()
llm = get_llm_engine()
app = create_retrieval_graph(emb, llm)

with st.sidebar:
    url = st.text_input("Swagger URL")
    if st.button("DB 동기화"):
        count = sync_swagger(url, emb)
        st.success(f"{count}개 API 로드 완료")

if prompt := st.chat_input("질문을 입력하세요"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        result = app.invoke({"question": prompt})
        st.write(result["generation"])
        
        with st.expander("📍 근거 문서 및 유사도"):
            for doc in result["documents"]:
                st.caption(f"**{doc.metadata['method'].upper()} {doc.metadata['path']}** (유사도: {doc.metadata['score']}%)")
                st.text(doc.page_content)