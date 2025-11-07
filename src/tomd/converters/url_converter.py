"""URL to Markdown converter."""

from pathlib import Path
from typing import Union

import html2text
import requests
from bs4 import BeautifulSoup


class URLConverter:
    """Convert web pages to Markdown."""

    def __init__(self):
        self.converter = html2text.HTML2Text()
        # Configure html2text options
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_emphasis = False
        self.converter.body_width = 0  # Don't wrap lines
        self.converter.unicode_snob = True  # Use unicode characters
        self.converter.skip_internal_links = False

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

        # Fetch the web page
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url_str, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get the main content (try to find article or main content area)
        main_content = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", class_=lambda x: x and "content" in x.lower())
            or soup.find("body")
        )

        if main_content:
            html_content = str(main_content)
        else:
            html_content = str(soup)

        # Convert to markdown
        markdown = self.converter.handle(html_content)

        # Add source URL at the top
        result = f"# Source: {url_str}\n\n{markdown.strip()}"

        return result
