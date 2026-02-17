from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

def get_models():
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    llm = OllamaLLM(model="llama3")
    return embeddings, llm