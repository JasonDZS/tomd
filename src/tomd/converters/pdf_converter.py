"""PDF to Markdown converter."""

from pathlib import Path

from pypdf import PdfReader


class PDFConverter:
    """Convert PDF files to Markdown."""

    def convert(self, file_path: Path) -> str:
        """
        Convert a PDF file to Markdown.

        Args:
            file_path: Path to the PDF file

        Returns:
            Markdown string representation
        """
        reader = PdfReader(file_path)

        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                # Add page separator for multi-page documents
                if page_num > 1:
                    text_parts.append(f"\n\n---\n\n## Page {page_num}\n\n")
                text_parts.append(text)

        return "".join(text_parts).strip()
