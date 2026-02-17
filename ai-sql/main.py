import streamlit as st
from models import get_models
from database import sync_swagger
from graph import create_app

embeddings, llm = get_models()
app = create_app(embeddings, llm)

st.title("🛡️ 지능형 API 어시스턴트")

# 사이드바에서 데이터 동기화
with st.sidebar:
    url = st.text_input("Swagger URL")
    if st.button("동기화"):
        count = sync_swagger(url, embeddings)
        st.success(f"{count}개 API 로드 완료")

# 메인 채팅창
if prompt := st.chat_input("질문하세요"):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        result = app.invoke({"question": prompt, "iteration": 0})
        st.write(result["generation"])