
---

# 📘 [Total Docs] 로컬 AI SQL & Swagger 어시스턴트: 지능형 기술 지원 허브

본 문서는 **보안(Privacy)**과 **정확도(Accuracy)**를 동시에 잡기 위해 설계된 로컬 기반 RAG 시스템의 전체 명세입니다. 개발팀 내 공유 또는 프로젝트 포트폴리오의 기술 백서로 활용하기 최적화되어 있습니다.

---

## 1. 프로젝트 비전 및 핵심 가치 (Project Vision)

현대 소프트웨어 개발 환경에서 **API 명세(Swagger)**와 **데이터베이스 구조(SQL)**는 시시각각 변합니다. 본 프로젝트는 이러한 기술 자산을 AI가 실시간으로 학습하고 가이드하는 **'살아있는 문서'**를 지향합니다.

* **Privacy First:** 사내 자산인 SQL 쿼리와 API 구조는 외부 유출이 치명적입니다. **Ollama**를 통해 모든 추론을 로컬(Internal Network) 내에서 완결합니다.
* **Contextual Accuracy:** 단순 키워드 매칭의 한계를 넘어, **OpenAI (또는 Ollama)** 임베딩을 통해 문맥적 의미를 파악하여 가장 적절한 기술 정보를 매칭합니다.
* **Self-Correcting Logic:** **LangGraph**를 도입하여 AI가 스스로 자신의 답변을 검증하고, 부족할 경우 검색 전략을 수정하는 지능형 루프를 구현합니다.

---

## 2. 시스템 아키텍처 (System Architecture)

전체 시스템은 **[데이터 수집 -> 수치화 -> 저장 -> 추론 -> 검증 -> 응답]**의 6단계 파이프라인으로 구성됩니다.

1. **Data Ingestion:** Swagger JSON, SQL DDL, 테이블 정의서 등을 로드하여 의미 있는 단위(Chunk)로 분할합니다.
2. **Embedding (Vectorization):** 선택된 모델(OpenAI 또는 로컬 Ollama)이 텍스트를 고차원 벡터로 변환합니다.
3. **Vector Store:** 변환된 벡터와 원본 텍스트, 메타데이터를 **Chroma DB**에 인덱싱하여 저장합니다.
4. **Reasoning (LangGraph):** 질문이 들어오면 질문의 카테고리를 분류(Router)하고, 검색된 정보의 관련성을 점수화(Grader)합니다.
5. **Generation:** **Ollama(Llama3)**가 최종적으로 검증된 정보를 바탕으로 자연어 답변을 생성합니다.

---

## 3. 심층 기술 스택 (Deep-Dive Tech Stack)

| 계층 | 기술명 | 상세 역할 및 선정 이유 |
| --- | --- | --- |
| **LLM Engine** | **Ollama / OpenAI** | 고성능 모델을 로컬 또는 클라우드 API로 구동. 유연한 인프라 선택 가능. |
| **Embedding** | **OpenAI / Ollama** | 문맥 검색을 위한 임베딩 레이어. 환경 변수(`OPENAI_BASE_URL`)에 따라 동적으로 엔진 선택. |
| **Vector DB** | **Chroma DB** | 임베딩 데이터와 메타데이터를 통합 관리하는 오픈소스 벡터 저장소. 로컬 영속성 관리가 매우 용이함. |
| **Orchestration** | **LangChain / LangGraph** | 단순 체인(Chain)을 넘어, 상태(State)를 보존하고 조건부 분기(Edge)를 가진 복잡한 워크플로우 제어. |
| **UI Framework** | **Streamlit** | Python 기반 웹 프레임워크. 데이터 시각화 및 대화형 인터페이스를 빠르게 구현. |

---

## 4. 이론적 배경 (Theoretical Background)

### 📐 유사도 측정: 코사인 유사도 ()

Vector DB는 텍스트를 좌표 공간상의 점으로 인식합니다. 두 문장이 얼마나 비슷한지는 벡터 사이의 각도()를 통해 계산합니다.

값이 **1**에 가까울수록 두 기술 문서의 맥락이 일치함을 의미합니다.

### 🔄 LangGraph의 순환 구조 (Cycle)

기본적인 RAG(LangChain)는 일직선으로 진행되지만, **LangGraph**는 **'검증(Evaluation)'** 단계를 추가합니다.

* **Problem:** 검색 결과가 질문과 관련 없는 엉뚱한 SQL을 가져온 경우.
* **Solution:** LangGraph의 노드(Node)가 이를 감지하여 다시 검색을 지시하거나, 사용자에게 "더 구체적인 테이블명을 말씀해 주세요"라고 되묻습니다.

---

## 5. 단계별 구축 로드맵 (Detailed Roadmap)

### 1단계: 데이터 최적화 (Data Strategy)

AI의 성능은 데이터 품질에 비례합니다.

* **Swagger 최적화:** `GET /users` 같은 경로보다 `summary: "전체 사용자 목록 조회"`, `description: "활성 상태인 유저의 페이징 목록을 반환합니다"`와 같이 인간 친화적인 설명을 추가합니다.
* **Metadata 주입:** 각 벡터에 `API_VERSION`, `LAST_UPDATED`, `DB_SCHEMA` 등의 메타데이터를 붙여 검색 결과의 신뢰도를 높입니다.

### 2단계: 하이브리드 검색 구현 (Embedding)

**OpenAI/Ollama**의 특징을 활용하여 검색을 수행합니다.

* **Dense Search:** 질문의 '의미'를 찾아내어 벡터 공간에서 유사한 문서를 검색합니다.

### 3단계: 지능형 RAG 체인 (Reranking & Logic)

단순 검색 결과 상위 5개를 LLM에 던지는 대신, **Reranker**를 도입하여 순위를 재조정합니다.

* 검색 결과가 10개라면, Reranker 모델이 질문과 각 문서를 다시 1:1로 대조하여 가장 정답에 가까운 3개만 추려냅니다.

---

## 6. 설치 및 실행 가이드 (Setup)

### 1. 모델 준비 및 가동

로컬 터미널에서 다음을 실행하여 엔진을 준비합니다.

```bash
ollama pull llama3

```

### 2. 환경 구축

```bash
# 핵심 라이브러리 설치
pip install langchain langchain-openai langchain-ollama \
            langchain-community chromadb streamlit langgraph

```

### 3. 서비스 실행

```bash
streamlit run main.py --server.address 0.0.0.0 --server.port 5415

```

---

## 🛠️ 요약하자면:

* **데이터가 들어올 때:** main.py -> database.py -> models.py(Embedding) 순으로 작동.
* **질문을 던졌을 때:** main.py -> graph.py(워크플로우 가동) -> models.py(LLM) 순으로 작동.
* 이 구조는 협업 시에도 유리합니다. 예를 들어, "답변을 더 친절하게 바꾸고 싶어"라면 **graph.py**의 프롬프트만 고치면 되고, "데이터 저장 방식을 바꾸고 싶어"라면 **database.py**만 고치면 됩니다.