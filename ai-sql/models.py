from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os

# 임베딩 모델 로드: OPENAI_BASE_URL 환경 변수가 있으면 OpenAI (혹은 호환 API), 없으면 로컬 Ollama 사용
def get_embeddings(api_url=None, api_key=None):
    base_url = api_url or os.getenv("OPENAI_BASE_URL")
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    if base_url:
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_base=base_url,
            openai_api_key=api_key if api_key else "no-key"
        )
    else:
        # 로컬 Ollama의 기본 임베딩 모델 (nomic-embed-text 추천)
        return OllamaEmbeddings(model="nomic-embed-text")

# 전략 패턴(Strategy Pattern)이 적용
# 사용자가 UI에서 선택한 값에 따라 ChatOllama(로컬) 객체를 만들지, ChatOpenAI(외부 API) 객체를 만들지 동적으로 결정
# temperature=0 설정은 AI가 창의적이기보다 **'사실에 기반한 정확한 답변'**을 하도록
def get_llm_engine(model_name, api_url=None, api_key=None):
    base_url = api_url or os.getenv("OPENAI_BASE_URL")
    api_key = api_key or os.getenv("OPENAI_API_KEY")

    if base_url:
        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key if api_key else "no-key",
            openai_api_base=base_url,
            temperature=0
        )
    else:
        return ChatOllama(model=model_name, temperature=0)