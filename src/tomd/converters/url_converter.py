"""URL to Markdown converter."""

from pathlib import Path
from typing import Optional, Union

import html2text
import requests
from bs4 import BeautifulSoup
from loguru import logger


class URLConverter:
    """Convert web pages to Markdown."""

    def __init__(self, use_browser: bool = False, content_selector: Optional[str] = None):
        self.use_browser = use_browser
        self.content_selector = content_selector
        self.converter = html2text.HTML2Text()
        # Configure html2text options
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_emphasis = False
        self.converter.body_width = 0
        self.converter.unicode_snob = True
        self.converter.skip_internal_links = False

    def _fetch_with_browser(self, url: str) -> str:
        """Fetch page content using headless browser."""
        from playwright.sync_api import sync_playwright

        logger.info(f"Using headless browser to fetch: {url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            html_content = page.content()
            browser.close()

        logger.debug(f"Browser fetch completed, content length: {len(html_content)}")
        return html_content

    def _fetch_with_requests(self, url: str) -> str:
        """Fetch page content using requests."""
        logger.info(f"Using requests to fetch: {url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        logger.debug(f"Requests fetch completed, status: {response.status_code}")
        return response.text

    def _extract_content(self, html: str) -> str:
        """Extract main content from HTML."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Use custom selector if provided
        if self.content_selector:
            logger.debug(f"Using custom selector: {self.content_selector}")
            main_content = soup.select_one(self.content_selector)
            if not main_content:
                logger.warning(f"Selector '{self.content_selector}' not found, using fallback")
                main_content = soup.find("body")
        else:
            # Auto-detect main content
            main_content = (
                soup.find("article")
                or soup.find("main")
                or soup.find("div", class_=lambda x: x and "content" in x.lower())
                or soup.find("body")
            )

        return str(main_content) if main_content else str(soup)

    def convert(self, url: Union[str, Path]) -> str:
        """
        Convert a web page to Markdown.

        Args:
            url: URL of the web page to convert

        Returns:
            Markdown string representation

        Raises:
            requests.RequestException: If the URL cannot be fetched
        """
        url_str = str(url)

        # Fetch HTML content
        if self.use_browser:
            html_content = self._fetch_with_browser(url_str)
        else:
            html_content = self._fetch_with_requests(url_str)

        # Extract main content
        extracted_html = self._extract_content(html_content)

        # Convert to markdown
        markdown = self.converter.handle(extracted_html)

        # Add source URL at the top
        result = f"# Source: {url_str}\n\n{markdown.strip()}"

        return result
