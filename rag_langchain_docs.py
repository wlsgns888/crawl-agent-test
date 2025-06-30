
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from firecrawl import FirecrawlApp, ScrapeOptions
from langchain_core.documents import Document

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Firecrawl API 키 확인
if not os.getenv("FIRECRAWL_API_KEY"):
    raise ValueError("FIRECRAWL_API_KEY environment variable not set.")

# LLM 및 Embeddings 초기화
llm = ChatOpenAI(model="gpt-4o", temperature=0)
embeddings = OpenAIEmbeddings()

# FirecrawlApp 인스턴스 생성
firecrawl_app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def get_langchain_docs_data(url: str, limit: int = 5):
    print(f"Crawling {url} with limit {limit}...")
    
    # ScrapeOptions 객체 생성 및 enableJavascript 설정
    # Langchain 문서는 정적 페이지이므로 enableJavascript는 필요 없을 수 있지만, 
    # 혹시 모를 경우를 대비하여 남겨둡니다.
    scrape_options = ScrapeOptions(enableJavascript=True)
    
    crawled_data_result = firecrawl_app.crawl_url(url, limit=limit, scrape_options=scrape_options)
    documents = crawled_data_result.data
    
    # Langchain Document 형식으로 변환
    langchain_documents = []
    for doc in documents:
        if doc.markdown: # 마크다운 내용이 있는 경우에만 추가
            langchain_documents.append(Document(
                page_content=doc.markdown,
                metadata={
                    "source": doc.metadata.get('sourceURL', url),
                    "title": doc.metadata.get('title', 'No Title')
                }
            ))
    print(f"Crawled {len(langchain_documents)} documents.")
    return langchain_documents

def create_vector_store(documents):
    print("Creating vector store...")
    if not documents:
        print("No documents to create vector store from.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    if not chunks:
        print("No chunks generated from documents.")
        return None

    vector_store = FAISS.from_documents(chunks, embeddings)
    print("Vector store created.")
    return vector_store

def create_rag_chain(vector_store):
    print("Creating RAG chain...")
    if vector_store is None:
        print("Vector store is None, cannot create RAG chain.")
        return None

    retriever = vector_store.as_retriever()
    
    prompt = ChatPromptTemplate.from_template(
        """Answer the following question based only on the provided context:
        <context>
        {context}
        </context>
        Question: {input}"""
    )
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    print("RAG chain created.")
    return retrieval_chain

if __name__ == "__main__":
    langchain_docs_url = "https://python.langchain.com/"
    
    # 1. 정보 수집 (Crawl)
    langchain_docs = get_langchain_docs_data(langchain_docs_url, limit=3) # 3페이지 크롤링
    
    # 2. 색인 (Indexing)
    vector_store = create_vector_store(langchain_docs)
    
    # 3. 검색 및 답변 생성 (Retrieve & Generate)
    if vector_store:
        rag_chain = create_rag_chain(vector_store)
        
        # 테스트 쿼리
        query = "Langchain은 무엇이며, 어떤 주요 구성 요소로 이루어져 있나요?"
        print(f"\nUser Query: {query}")
        
        try:
            if rag_chain:
                response = rag_chain.invoke({"input": query})
                print(f"\nAgent Response: {response['answer']}")
            else:
                print("RAG chain could not be created.")
        except Exception as e:
            print(f"An error occurred during RAG chain invocation: {e}")
    else:
        print("Vector store could not be created. RAG process aborted.")
