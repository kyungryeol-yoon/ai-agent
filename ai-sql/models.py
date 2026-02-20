import os
import httpx
from openai import OpenAI
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings

def get_custom_client(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # SSL 검증 무시 및 커스텀 헤더 설정
    return httpx.Client(verify=False, headers=headers)

class CustomInternalEmbeddings(Embeddings):
    def __init__(self, api_url, api_key):
        self.http_client = get_custom_client(api_key)
        self.client = OpenAI(base_url=api_url, api_key=api_key, http_client=self.http_client)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(input=texts, model="bge-m3")
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def get_embeddings():
    return CustomInternalEmbeddings(
        api_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

def get_llm_engine(model_name="llama3"):
    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(
        model=model_name,
        openai_api_base=api_base,
        openai_api_key=api_key,
        temperature=0,
        http_client=get_custom_client(api_key)
    )