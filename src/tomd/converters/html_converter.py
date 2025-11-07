"""HTML to Markdown converter."""

from pathlib import Path

import html2text


class HTMLConverter:
    """Convert HTML files to Markdown."""

    def __init__(self):
        self.converter = html2text.HTML2Text()
        # Configure html2text options
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_emphasis = False
        self.converter.body_width = 0  # Don't wrap lines
        self.converter.unicode_snob = True  # Use unicode characters
        self.converter.skip_internal_links = False

    def convert(self, file_path: Path) -> str:
        """
        Convert an HTML file to Markdown.

        Args:
            file_path: Path to the HTML file

        Returns:
            Markdown string representation
        """
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        markdown = self.converter.handle(html_content)
        return markdown.strip()
