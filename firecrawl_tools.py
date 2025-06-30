
import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import json

# .env 파일에서 환경 변수 로드
load_dotenv()

class ScrapeURLInput(BaseModel):
    url: str = Field(description="The URL to scrape.")

class FirecrawlScrapeTool(BaseTool):
    name: str = "firecrawl_scrape_url"
    description: str = "하나의 웹 페이지 URL을 입력받아 광고나 방해 요소를 제거한 핵심 콘텐츠를 텍스트(Markdown) 형식으로 반환합니다. 특정 페이지의 내용을 정확히 가져와야 할 때 사용하세요."
    args_schema: type[BaseModel] = ScrapeURLInput

    def _run(self, url: str) -> str:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        try:
            scraped_data = app.scrape_url(url)
            return scraped_data.markdown
        except Exception as e:
            return f"Error scraping URL: {e}"

class CrawlURLInput(BaseModel):
    url: str = Field(description="The starting URL to crawl.")
    limit: Optional[int] = Field(default=10, description="Maximum number of pages to crawl.")

class FirecrawlCrawlTool(BaseTool):
    name: str = "firecrawl_crawl_website"
    description: str = "시작 URL을 입력받아 해당 웹사이트를 순회(crawling)하며 여러 페이지의 정보를 수집합니다. 웹사이트 전반의 정보나 특정 주제에 대한 여러 페이지의 데이터가 필요할 때 사용하세요. 크롤링 깊이나 최대 페이지 수 같은 파라미터를 함께 지정할 수 있습니다."
    args_schema: type[BaseModel] = CrawlURLInput

    def _run(self, url: str, limit: Optional[int] = 10) -> str:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        try:
            crawled_data_result = app.crawl_url(url, limit=limit)
            documents = crawled_data_result.data
            result_str = ""
            for i, doc in enumerate(documents):
                result_str += f"--- Crawled Page {i+1} ---\n"
                result_str += f"Source: {doc.metadata['sourceURL']}\n"
                result_str += f"Markdown: {doc.markdown[:500]}...\n\n" # Limit markdown output for brevity
            return result_str
        except Exception as e:
            return f"Error crawling URL: {e}"

if __name__ == "__main__":
    # Test Scrape Tool
    print("--- Testing FirecrawlScrapeTool ---")
    scrape_tool = FirecrawlScrapeTool()
    scrape_result = scrape_tool.run(tool_input="https://python.langchain.com/v0.2/docs/introduction/")
    print(scrape_result[:1000]) # Print first 1000 chars for brevity

    print("\n--- Testing FirecrawlCrawlTool ---")
    crawl_tool = FirecrawlCrawlTool()
    crawl_result = crawl_tool.run(tool_input={"url": "https://python.langchain.com/", "limit": 2})
    print(crawl_result)
