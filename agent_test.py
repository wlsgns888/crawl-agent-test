

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent # Changed import
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from firecrawl_tools import FirecrawlScrapeTool, FirecrawlCrawlTool

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Firecrawl 도구 초기화
tools = [
    FirecrawlScrapeTool(),
    FirecrawlCrawlTool()
]

# 프롬프트 정의 (OpenAI Functions Agent에 맞게 간소화)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant that can interact with websites using Firecrawl tools."),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 에이전트 생성 (create_openai_functions_agent 사용)
agent = create_openai_functions_agent(llm, tools, prompt) # Changed agent creation

# 에이전트 실행기 생성
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    print("Langchain Firecrawl Agent Test")
    test_query = "https://python.langchain.com/v0.2/docs/introduction/ 이 페이지의 내용을 요약해줘."
    print(f"\nUser: {test_query}")
    
    try:
        response = agent_executor.invoke({"input": test_query})
        print(f"Agent: {response['output']}")
    except Exception as e:
        print(f"An error occurred: {e}")
