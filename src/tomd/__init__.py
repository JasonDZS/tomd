"""Convert various file formats to Markdown."""

from pathlib import Path
from typing import Union

from .converters import get_converter
from .converters.url_converter import URLConverter


def _is_url(input_str: str) -> bool:
    """Check if the input string is a URL."""
    return input_str.startswith(("http://", "https://"))


def tomd(file: Union[str, Path]) -> str:
    """
    Convert a file or URL to Markdown format.

    Args:
        file: Path to the file to convert, or a URL (http:// or https://)

    Returns:
        Markdown string representation of the file content

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file format is not supported
        requests.RequestException: If the URL cannot be fetched
    """
    input_str = str(file)

    # Check if input is a URL
    if _is_url(input_str):
        converter = URLConverter()
        return converter.convert(input_str)

    # Handle as file path
    file_path = Path(file)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file}")

    # Get the appropriate converter based on file extension
    converter = get_converter(file_path)

    # Convert to markdown
    return converter.convert(file_path)


__all__ = ["tomd"]
