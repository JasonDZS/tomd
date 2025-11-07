"""Text to Markdown converter."""

from pathlib import Path


class TextConverter:
    """Convert plain text files to Markdown."""

    def convert(self, file_path: Path) -> str:
        """
        Convert a plain text file to Markdown.

        For plain text and markdown files, we simply return the content as-is.

        Args:
            file_path: Path to the text file

        Returns:
            Content of the file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return content.strip()
