# tomd

Convert various file formats to Markdown.

## Features

- Simple API: just one function `tomd(file)`
- Supports multiple file formats:
  - HTML (.html, .htm)
  - PDF (.pdf)
  - DOCX (.docx)
  - Plain text (.txt)
  - Markdown (.md)
  - **Web URLs** (http://, https://)
- Extensible plugin architecture for adding new formats
- Type-safe with full type hints
- Comprehensive test coverage

## Installation

```bash
pip install tomd
```

Or with uv:

```bash
uv add tomd
```

## Usage

```python
from tomd import tomd

# Convert an HTML file to Markdown
md_result = tomd(file="example.html")
print(md_result)

# Convert a URL to Markdown
md_result = tomd(file="https://huggingface.co/blog/lerobotxnvidia-healthcare")
print(md_result)

# Works with Path objects too
from pathlib import Path
md_result = tomd(file=Path("example.html"))
```

## Supported Formats

| Format | Extensions/Protocol | Description |
|--------|-----------|-------------|
| HTML | .html, .htm | Converts HTML to Markdown preserving structure |
| PDF | .pdf | Extracts text from PDF files and converts to Markdown |
| DOCX | .docx | Converts Word documents to Markdown with formatting, tables, and headings |
| Text | .txt | Returns plain text as-is |
| Markdown | .md | Returns markdown content unchanged |
| **Web URLs** | http://, https:// | Fetches and converts web pages to Markdown, removing scripts/styles and extracting main content |

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tomd.git
cd tomd

# Install dependencies
uv sync --extra dev
```

### Running Tests

```bash
uv run pytest tests/ -v
```

### Adding New Format Support

To add support for a new file format:

1. Create a new converter in `src/tomd/converters/`
2. Implement the `convert(file_path: Path) -> str` method
3. Register the converter in `src/tomd/converters/__init__.py`
4. Add tests for the new format

Example:

```python
# src/tomd/converters/my_converter.py
from pathlib import Path

class MyConverter:
    def convert(self, file_path: Path) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Convert content to markdown
        return markdown_content
```

## License

Apache License 2.0
