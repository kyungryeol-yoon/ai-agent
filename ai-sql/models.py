from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

# 텍스트를 숫자로 바꾸는 모델(BGE-M3)을 로드 . 한 번 로드하면 Vector DB에 저장할 때와 검색할 때 동일하게 사용
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

# 전략 패턴(Strategy Pattern)이 적용
# 사용자가 UI에서 선택한 값에 따라 ChatOllama(로컬) 객체를 만들지, ChatOpenAI(외부 API) 객체를 만들지 동적으로 결정
# temperature=0 설정은 AI가 창의적이기보다 **'사실에 기반한 정확한 답변'**을 하도록
def get_llm_engine(llm_type, model_name, api_url=None, api_key=None):
    if llm_type == "Local (Ollama)":
        return ChatOllama(model=model_name, temperature=0)
    else:
        # 외부 API (OpenAI 규격 호환)
        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key if api_key else "no-key",
            openai_api_base=api_url,
            temperature=0
        )