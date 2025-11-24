from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://openai.com/index/intuit-partnership/"

with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")

# Check for common content containers
print("=== Checking for content containers ===")
print(f"article: {soup.find('article') is not None}")
print(f"main: {soup.find('main') is not None}")

# Find divs with content-related classes
content_divs = soup.find_all('div', class_=lambda x: x and any(
    keyword in str(x).lower() for keyword in ['content', 'post', 'article', 'blog']
))
print(f"\nFound {len(content_divs)} divs with content-related classes:")
for div in content_divs[:5]:
    classes = div.get('class', [])
    print(f"  - {' '.join(classes)}")

# Check for specific OpenAI structure
if soup.find('article'):
    article = soup.find('article')
    print(f"\n=== Article found ===")
    print(f"Article classes: {article.get('class', [])}")
    print(f"Article content length: {len(str(article))}")
