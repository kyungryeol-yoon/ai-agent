import streamlit as st
from models import get_embeddings, get_llm_engine
from database import sync_swagger
from graph import create_retrieval_graph

st.set_page_config(page_title="API AI Assistant", layout="wide")

# 1. 사이드바 - 설정 영역
# st.sidebar: 설정 창입니다. 여기서 모델을 바꾸거나 새로운 Swagger URL을 넣어 지식을 업데이트합니다.
with st.sidebar:
    st.header("⚙️ 모델 및 데이터 설정")
    
    # LLM 선택 UI
    llm_type = st.selectbox("LLM 엔진", ["Local (Ollama)", "External API"])
    if llm_type == "Local (Ollama)":
        m_name = st.text_input("Ollama 모델명", value="llama3")
        api_url, api_key = None, None
    else:
        api_url = st.text_input("API URL", value="https://api.openai.com/v1")
        m_name = st.text_input("모델명", value="gpt-4o")
        api_key = st.text_input("API Key", type="password")

    st.divider()
    
    # Swagger 동기화 UI
    sw_url = st.text_input("Swagger JSON URL")
    if st.button("지식베이스 동기화"):
        emb = get_embeddings(api_url, api_key)
        try:
            count = sync_swagger(sw_url, emb)
            st.success(f"{count}개 API 명세가 로드되었습니다!")
        except Exception as e:
            st.error(e)

# 2. 메인 채팅 영역
st.title("🛡️ Self-Correction API Assistant")
st.caption("Swagger 문서를 바탕으로 AI가 판단하고 답변합니다.")

# 모델 로드 (캐싱을 통해 속도 향상 가능하나 여기선 직관적으로 표현)
embeddings = get_embeddings(api_url, api_key)
llm = get_llm_engine(llm_type, m_name, api_url, api_key)
app = create_retrieval_graph(embeddings, llm)

# st.session_state.messages: 대화 기록을 유지합니다. Streamlit은 새로고침이 잦기 때문에 이 변수에 기록을 쌓아두어야 대화가 끊기지 않습니다.
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # st.spinner: AI가 '생각(채점 및 재검색)'하는 동안 사용자에게 "기다려 주세요"라는 시각적 피드백을 줍니다.
        with st.spinner("AI가 지식을 검증하며 답변을 생성 중입니다..."):
            # app.invoke(): 사용자가 질문을 입력하면 LangGraph 워크플로우를 가동시키는 스위치 역할을 합니다.
            result = app.invoke({"question": prompt, "iteration": 0})
            ans = result["generation"]
            st.markdown(ans)
            if result["iteration"] > 1:
                st.info("💡 초기 검색 결과가 부족하여 재구성된 질문으로 다시 검색하였습니다.")
                
    st.session_state.messages.append({"role": "assistant", "content": ans})