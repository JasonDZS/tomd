"""Convert various file formats to Markdown."""

from pathlib import Path
from typing import Optional, Union

from loguru import logger

from .converters import get_converter
from .converters.url_converter import URLConverter
from .llm_enhancer import enhance_markdown


def _is_url(input_str: str) -> bool:
    """Check if the input string is a URL."""
    return input_str.startswith(("http://", "https://"))


def tomd(
    file: Union[str, Path],
    llm_enhance: bool = False,
    language: Optional[str] = None,
) -> str:
    """
    Convert a file or URL to Markdown format.

    Args:
        file: Path to the file to convert, or a URL (http:// or https://)
        llm_enhance: Whether to enhance the content using LLM (default: False)
                    Requires OPENAI_API_KEY to be set in .env file
        language: Target language for translation (e.g., "Chinese", "English", "Japanese")
                 Only used when llm_enhance=True. If None, content will be enhanced without translation

    Returns:
        Markdown string representation of the file content

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file format is not supported or API key is missing
        requests.RequestException: If the URL cannot be fetched
        Exception: If LLM enhancement fails

    Examples:
        >>> # Basic conversion
        >>> tomd("example.html")

        >>> # Convert with LLM enhancement
        >>> tomd("example.html", llm_enhance=True)

        >>> # Convert and translate to Chinese
        >>> tomd("https://example.com", llm_enhance=True, language="Chinese")
    """
    input_str = str(file)
    logger.info(f"Starting conversion for: {input_str}")

    # Check if input is a URL
    if _is_url(input_str):
        logger.info(f"Detected URL input: {input_str}")
        converter = URLConverter()
        markdown_content = converter.convert(input_str)
        logger.success(f"URL conversion completed, content length: {len(markdown_content)}")
    else:
        # Handle as file path
        file_path = Path(file)
        logger.info(f"Processing file: {file_path}")

        if not file_path.exists():
            logger.error(f"File not found: {file}")
            raise FileNotFoundError(f"File not found: {file}")

        if not file_path.is_file():
            logger.error(f"Path is not a file: {file}")
            raise ValueError(f"Path is not a file: {file}")

        # Get the appropriate converter based on file extension
        converter = get_converter(file_path)
        logger.debug(f"Using converter: {converter.__class__.__name__}")

        # Convert to markdown
        markdown_content = converter.convert(file_path)
        logger.success(f"File conversion completed, content length: {len(markdown_content)}")

    # Apply LLM enhancement if requested
    if llm_enhance:
        logger.info(f"Applying LLM enhancement (language: {language or 'None'})")
        markdown_content = enhance_markdown(
            markdown_content, language=language, enabled=True
        )
        logger.success("LLM enhancement completed")

    return markdown_content


__all__ = ["tomd"]
