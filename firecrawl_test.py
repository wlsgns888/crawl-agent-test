import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# .env 파일에서 환경 변수 로드
load_dotenv()

# FirecrawlApp 인스턴스 생성
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# 1. Scrape 기능 테스트
print("--- Testing Firecrawl Scrape ---")
scraped_data = app.scrape_url('https://python.langchain.com/v0.2/docs/introduction/')
print(scraped_data.markdown)


# 2. Crawl 기능 테스트
print("\n--- Testing Firecrawl Crawl ---")
crawled_data_result = app.crawl_url('https://python.langchain.com/v0.2/docs/introduction/', limit=3)

# The actual documents are in the .data attribute of the result object
documents = crawled_data_result.data
for i, data in enumerate(documents):
    print(f"\n--- Crawled Page {i+1} ---")
    # The source URL is in the metadata
    print(f"Source: {data.metadata['sourceURL']}")
    # Print the first 200 characters of the markdown
    print(f"Markdown: {data.markdown[:200]}...")