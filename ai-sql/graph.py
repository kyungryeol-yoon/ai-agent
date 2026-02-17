from typing import List, TypedDict
from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma

# GraphState: AI가 대화 중에 기억해야 할 주머니입니다. (질문, 검색된 문서, 답변, 재시도 횟수)

class GraphState(TypedDict):
    question: str
    generation: str
    documents: List
    iteration: int

def create_retrieval_graph(embeddings, llm):
    # --- 노드 1: 검색 ---
    # retrieve: 질문과 관련된 API 명세를 DB에서 $k$개 찾아옵니다.
    def retrieve(state):
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        docs = vectorstore.as_retriever(search_kwargs={"k": 3}).invoke(state["question"])
        return {"documents": docs, "iteration": state.get("iteration", 0) + 1}

    # --- 노드 2: 채점 (판단) ---
    # grade_documents: [핵심] AI가 검색된 결과를 보고 "이게 정말 질문이랑 상관있나?"를 판단합니다. 쓸모없는 정보는 여기서 걸러집니다.
    def grade_documents(state):
        prompt = ChatPromptTemplate.from_template(
            "당신은 문서가 질문과 관련있는지 채점하는 전문가입니다.\n질문: {question}\n문서: {doc}\n관련있으면 'yes', 없으면 'no'라고만 답하세요."
        )
        chain = prompt | llm | StrOutputParser()
        
        relevant_docs = []
        for d in state["documents"]:
            score = chain.invoke({"question": state["question"], "doc": d.page_content})
            if "yes" in score.lower():
                relevant_docs.append(d)
        return {"documents": relevant_docs}

    # --- 노드 3: 답변 생성 ---
    # generate: 최종적으로 걸러진 고품질 정보만 가지고 한국어로 답변을 생성합니다.
    def generate(state):
        prompt = ChatPromptTemplate.from_template(
            """당신은 API 명세 전문가입니다. 아래 제공된 문맥(Context)만을 사용하여 사용자의 질문에 답하세요.
            
            [지침]
            1. 반드시 한국어로 답변하세요.
            2. 문맥에 답이 없으면 '제공된 문서에서 관련 정보를 찾을 수 없습니다'라고 답하세요.
            3. 기술적인 용어(Endpoint, Parameter 등)는 그대로 사용해도 좋지만, 설명은 한국어로 하세요.

            문맥: {context}
            질문: {question}
            
            한국어 답변:"""
        )
        context = "\n\n".join([d.page_content for d in state["documents"]])
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": state["question"]})
        return {"generation": response}

    # --- 노드 4: 질문 재구성 ---
    # rewrite: 만약 쓸모 있는 정보가 하나도 없다면, 질문을 더 구체적으로(예: "상세한 정보를 포함해서") 고쳐 씁니다.
    def rewrite(state):
        return {"question": f"더 상세한 API 정보를 포함해서 찾아줘: {state['question']}"}

    # --- 조건부 에지: 생성할지 재검색할지 결정 ---
    # 조건부 에지(decide_to_generate): "검색 결과가 있으면 답변으로 가고, 없으면 다시 검색(Loop)해!"라는 의사결정을 내립니다.
    def decide_to_generate(state):
        if not state["documents"] and state["iteration"] < 2:
            return "rewrite"
        return "generate"

    # 그래프 조립
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade", grade_documents)
    workflow.add_node("generate", generate)
    workflow.add_node("rewrite", rewrite)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade")
    workflow.add_conditional_edges("grade", decide_to_generate, {"rewrite": "rewrite", "generate": "generate"})
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("generate", END)

    return workflow.compile()