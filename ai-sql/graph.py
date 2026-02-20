from typing import List, TypedDict
from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma

class GraphState(TypedDict):
    question: str
    generation: str
    documents: List
    iteration: int

def create_retrieval_graph(embeddings, llm):
    def retrieve(state):
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        # 유사도 점수와 함께 검색
        docs_with_scores = vectorstore.similarity_search_with_score(state["question"], k=3)
        
        documents = []
        for doc, score in docs_with_scores:
            doc.metadata["score"] = round((1 - score) * 100, 2) # 거리 -> 유사도 변환
            documents.append(doc)
        return {"documents": documents, "iteration": state.get("iteration", 0) + 1}

    def generate(state):
        prompt = ChatPromptTemplate.from_template("문맥: {context}\n질문: {question}\n답변:")
        context = "\n".join([d.page_content for d in state["documents"]])
        ans = (prompt | llm | StrOutputParser()).invoke({"context": context, "question": state["question"]})
        return {"generation": ans}

    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()