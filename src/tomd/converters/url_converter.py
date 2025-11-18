"""URL to Markdown converter."""

import re
import tempfile
from pathlib import Path
from typing import Optional, Union

import html2text
import requests
from bs4 import BeautifulSoup
from loguru import logger

from .pdf_converter import PDFConverter


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

    def _is_arxiv_url(self, url: str) -> bool:
        """Check if URL is an arXiv paper."""
        return bool(re.search(r'arxiv\.org/(abs|pdf)/\d+\.\d+', url))

    def _is_douyin_url(self, url: str) -> bool:
        """Check if URL is a Douyin video."""
        return 'douyin.com' in url

    def _get_arxiv_pdf_url(self, url: str) -> str:
        """Convert arXiv URL to PDF download URL."""
        match = re.search(r'arxiv\.org/(abs|pdf)/(\d+\.\d+)', url)
        if match:
            paper_id = match.group(2)
            return f"https://arxiv.org/pdf/{paper_id}.pdf"
        return url

    def _download_pdf(self, url: str) -> Path:
        """Download PDF to temporary file."""
        logger.info(f"Downloading PDF from: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(response.content)
        temp_file.close()

        logger.debug(f"PDF downloaded to: {temp_file.name}")
        return Path(temp_file.name)

    def _fetch_with_browser(self, url: str) -> str:
        """Fetch page content using headless browser."""
        from playwright.sync_api import sync_playwright

        logger.info(f"Using headless browser to fetch: {url}")

        with sync_playwright() as p:
            browser = p.webkit.launch(headless=False if self._is_douyin_url(url) else True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )

            if self._is_douyin_url(url):
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                logger.info("Waiting for video content to load (30s for manual login if needed)...")
                try:
                    page.wait_for_selector("video", timeout=30000)
                    logger.info("Video element found, extracting content...")
                except Exception:
                    logger.warning("Video not found after 30s, extracting available content")
                page.wait_for_timeout(2000)
            else:
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

        # Handle arXiv papers
        if self._is_arxiv_url(url_str):
            logger.info(f"Detected arXiv paper: {url_str}")
            pdf_url = self._get_arxiv_pdf_url(url_str)
            pdf_path = self._download_pdf(pdf_url)

            try:
                pdf_converter = PDFConverter()
                markdown = pdf_converter.convert(pdf_path)
                result = f"# Source: {url_str}\n\n{markdown.strip()}"
                return result
            finally:
                pdf_path.unlink()

        # Fetch HTML content with automatic fallback
        if self.use_browser:
            html_content = self._fetch_with_browser(url_str)
        else:
            try:
                html_content = self._fetch_with_requests(url_str)
            except requests.RequestException as e:
                logger.warning(f"Requests failed ({e}), falling back to browser")
                html_content = self._fetch_with_browser(url_str)

        # Extract main content
        extracted_html = self._extract_content(html_content)

        # Convert to markdown
        markdown = self.converter.handle(extracted_html)

        # Add source URL at the top
        result = f"# Source: {url_str}\n\n{markdown.strip()}"

        return result
