# Langchain & Firecrawl 연동 에이전트 개발

## 1. 프로젝트 개요
본 프로젝트는 최신 웹 스크래핑/크롤링 솔루션인 **Firecrawl**을 **Langchain** 생태계에 통합하고, 이를 활용하여 자연어 기반의 사용자 요청을 자율적으로 처리하는 지능형 에이전트를 구현하는 것을 목표로 합니다. 초기 계획에서는 무신사 웹사이트를 대상으로 RAG(Retrieval-Augmented Generation) 패턴의 활용 사례를 제시하고자 했으나, 무신사 웹사이트의 강력한 크롤링 방지 메커니즘으로 인해 **Langchain 공식 문서 웹사이트**를 대상으로 RAG 패턴을 구현하여 프로젝트의 실용성을 검증했습니다.

## 2. 구현 내용

### 2.1. Firecrawl 핵심 기능 검증
`firecrawl_test.py` 스크립트를 통해 Firecrawl의 `scrape` 및 `crawl` 기능이 정상적으로 동작하는 것을 확인했습니다.
- `scrape`: 단일 URL의 핵심 콘텐츠(Markdown) 추출.
- `crawl`: 지정된 시작 URL로부터 하위 페이지들을 순회하며 데이터 수집.

### 2.2. Langchain Tool 개발 (`firecrawl_tools.py`)
Firecrawl의 `scrape` 및 `crawl` 기능을 각각 Langchain의 `BaseTool`로 래핑(wrapping)하여 `FirecrawlScrapeTool`과 `FirecrawlCrawlTool`을 개발했습니다. 각 Tool은 `name`, `description`, `args_schema`를 명확히 정의하여 Langchain 에이전트가 활용할 수 있도록 했습니다.

### 2.3. 지능형 에이전트 구현 (`agent_test.py`)
개발된 Firecrawl Tool을 장착한 Langchain 에이전트를 구현했습니다. `create_openai_functions_agent`를 사용하여 LLM(ChatOpenAI)과 Firecrawl Tool을 연동했으며, 사용자의 자연어 요청을 이해하고 적절한 Tool을 선택하여 실행하는 에이전트의 동작을 확인했습니다.

### 2.4. 실용적 활용 사례 제시 (RAG 패턴 - `rag_langchain_docs.py`)
Langchain 공식 문서 웹사이트를 대상으로 간단한 RAG 패턴을 구현했습니다.
1.  **정보 수집 (Crawl):** `FirecrawlCrawlTool`을 사용하여 Langchain 공식 문서 웹사이트를 크롤링했습니다.
2.  **색인 (Indexing):** 크롤링된 문서들을 `RecursiveCharacterTextSplitter`로 청크(chunk)로 분할하고, `OpenAIEmbeddings`를 사용하여 벡터로 변환한 후 `FAISS` 벡터 저장소에 저장했습니다.
3.  **검색 및 답변 생성 (Retrieve & Generate):** 사용자 질문에 대해 벡터 저장소에서 가장 관련성 높은 정보를 검색하고, 검색된 정보를 바탕으로 LLM이 최종 답변을 생성하도록 구현했습니다.

## 3. 기술 스택
- **언어:** Python 3.9+
- **핵심 라이브러리:**
    - `langchain`, `langchain-openai`, `langchain-community`
    - `firecrawl-py`
    - `pydantic`, `python-dotenv`, `faiss-cpu`
- **API:**
    - Firecrawl API
    - OpenAI API

## 4. 실행 방법

1.  **가상 환경 설정 및 의존성 설치:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install langchain langchain-openai openai firecrawl-py python-dotenv langchain-community faiss-cpu
    ```

2.  **API 키 설정:**
    프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가합니다. `YOUR_OPENAI_API_KEY`와 `YOUR_FIRECRAWL_API_KEY`를 실제 API 키로 교체하세요.
    ```
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    FIRECRAWL_API_KEY="YOUR_FIRECRAWL_API_KEY"
    ```

3.  **Firecrawl 기능 테스트:**
    ```bash
    source .venv/bin/activate
    python firecrawl_test.py
    ```

4.  **Langchain Tool 테스트:**
    ```bash
    source .venv/bin/activate
    python firecrawl_tools.py
    ```

5.  **Langchain 에이전트 테스트:**
    ```bash
    source .venv/bin/activate
    python agent_test.py
    ```
    (스크립트 실행 후 질문을 입력하세요. 예: `https://python.langchain.com/v0.2/docs/introduction/ 이 페이지의 내용을 요약해줘.`) 

6.  **RAG 패턴 테스트 (Langchain 문서):**
    ```bash
    source .venv/bin/activate
    python rag_langchain_docs.py
    ```

## 5. 결론 및 시사점
본 프로젝트를 통해 Firecrawl과 Langchain을 성공적으로 연동하여 웹 데이터를 활용하는 지능형 에이전트를 구현할 수 있음을 확인했습니다. 특히, RAG 패턴을 통해 LLM이 최신 웹 정보를 기반으로 답변을 생성하는 능력을 효과적으로 시연했습니다. 무신사와 같은 동적이고 크롤링 방지 메커니즘이 강력한 웹사이트에 대한 데이터 수집은 여전히 도전 과제임을 확인했으며, 향후 더 발전된 크롤링 기술이나 특정 웹사이트에 최적화된 접근 방식이 필요할 수 있습니다.