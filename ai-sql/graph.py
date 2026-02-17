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

def create_app(embeddings, llm):
    # --- 노드 정의 ---
    def retrieve_node(state):
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        docs = vectorstore.as_retriever().invoke(state["question"])
        return {"documents": docs, "iteration": state.get("iteration", 0) + 1}

    def grade_node(state):
        grader_prompt = ChatPromptTemplate.from_template("문서: {doc}\n질문: {question}\n관련 'yes'/'no'?")
        chain = grader_prompt | llm | StrOutputParser()
        relevant_docs = [d for d in state["documents"] if "yes" in chain.invoke({"question": state["question"], "doc": d.page_content}).lower()]
        return {"documents": relevant_docs}

    def generate_node(state):
        prompt = ChatPromptTemplate.from_template("문맥: {context}\n질문: {question}\n답변:")
        context = "\n".join([d.page_content for d in state["documents"]])
        response = (prompt | llm | StrOutputParser()).invoke({"context": context, "question": state["question"]})
        return {"generation": response}

    # --- 그래프 조립 ---
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("generate", generate_node)
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade")
    workflow.add_conditional_edges("grade", lambda s: "generate" if s["documents"] else "retrieve") # 단순화 예시
    workflow.add_edge("generate", END)
    
    return workflow.compile()