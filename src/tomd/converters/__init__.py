"""Converter registry and base classes."""

from pathlib import Path
from typing import Protocol


class Converter(Protocol):
    """Protocol for file format converters."""

    @staticmethod
    def convert(file_path: Path) -> str:
        """Convert a file to Markdown format."""
        ...


def get_converter(file_path: Path) -> Converter:
    """
    Get the appropriate converter for a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        Converter instance for the file type

    Raises:
        ValueError: If the file format is not supported
    """
    from . import docx_converter, html_converter, pdf_converter, text_converter

    suffix = file_path.suffix.lower()

    # Map file extensions to converters
    converter_map = {
        ".html": html_converter.HTMLConverter,
        ".htm": html_converter.HTMLConverter,
        ".txt": text_converter.TextConverter,
        ".md": text_converter.TextConverter,
        ".pdf": pdf_converter.PDFConverter,
        ".docx": docx_converter.DOCXConverter,
    }

    converter_class = converter_map.get(suffix)

    if converter_class is None:
        supported = ", ".join(sorted(converter_map.keys()))
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: {supported}"
        )

    return converter_class()


__all__ = ["Converter", "get_converter"]
