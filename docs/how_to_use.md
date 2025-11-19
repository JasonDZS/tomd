# How to Use tomd

## Installation

```bash
pip install git+https://github.com/JasonDZS/tomd.git
```

### Optional Dependencies

For browser support (dynamic content):
```bash
pip install git+https://github.com/JasonDZS/tomd.git
playwright install webkit
```

For LLM enhancement:
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Basic Usage

```python
from tomd import tomd

# Convert any supported file or URL
markdown = tomd("path/to/file")
print(markdown)
```

## Supported Sources

### 1. URL Conversion

Convert web pages to markdown with automatic fallback support.

```python
# Basic URL conversion (auto-fallback to browser if blocked)
markdown = tomd("https://example.com")

# Force browser mode for JavaScript-heavy sites
markdown = tomd("https://example.com", use_browser=True)

# Extract specific content with CSS selector
markdown = tomd("https://example.com", content_selector="article.main")

# arXiv papers (auto-downloads and converts PDF)
markdown = tomd("https://arxiv.org/abs/2301.00001")
```

**Features:**
- Automatic fallback: If requests fails (403, etc.), automatically tries browser
- Supports dynamic content with Playwright
- Custom CSS selectors for targeted extraction
- Special handling for arXiv papers and Douyin videos

### 2. HTML Files

Convert local HTML files to markdown.

```python
markdown = tomd("document.html")
```

**Features:**
- Preserves links, images, and emphasis
- No line wrapping
- Unicode support

### 3. PDF Files

Convert PDF documents to markdown.

```python
markdown = tomd("paper.pdf")
```

**Features:**
- Extracts text content
- Preserves document structure

### 4. DOCX Files

Convert Microsoft Word documents to markdown.

```python
markdown = tomd("document.docx")
```

**Features:**
- Converts headings (Heading 1-6 � # ##)
- Preserves bold (**text**) and italic (*text*)
- Converts tables to markdown format

### 5. Text/Markdown Files

Pass through text and markdown files as-is.

```python
markdown = tomd("notes.txt")
markdown = tomd("readme.md")
```

## LLM Enhancement

Enhance and optionally translate content using LLM.

```python
# Enhance content quality
markdown = tomd("https://example.com", llm_enhance=True)

# Enhance and translate to Chinese
markdown = tomd("document.pdf", llm_enhance=True, language="Chinese")

# Enhance and translate to Japanese
markdown = tomd("article.html", llm_enhance=True, language="Japanese")
```

**Requirements:**
- Set `OPENAI_API_KEY` in `.env` file
- Supports any language for translation

## Advanced Examples

### URL with Browser and Selector

```python
# Extract blog post content only
markdown = tomd(
    "https://blog.example.com/post",
    use_browser=True,
    content_selector=".post-content"
)
```

### Full Pipeline with Enhancement

```python
# Convert, enhance, and translate
markdown = tomd(
    "https://example.com/article",
    use_browser=True,
    llm_enhance=True,
    language="Chinese"
)
```

### Batch Processing

```python
from pathlib import Path

files = Path("docs").glob("*.html")
for file in files:
    markdown = tomd(file)
    output = file.with_suffix(".md")
    output.write_text(markdown)
```

## Error Handling

```python
try:
    markdown = tomd("https://example.com")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Conversion failed: {e}")
```

## Site-Specific Rules

Configure content selectors for different websites using a rule file.

### Using Default rule.yml

Create `rule.yml` in project root:

```yaml
sites:
  - domain: cognition.ai
    selector: "#blog-post__body"
  - domain: medium.com
    selector: "article"
  - domain: substack.com
    selector: ".post-content"
```

```python
# Automatically uses rule.yml
markdown = tomd("https://cognition.ai/blog/...")
```

### Using Custom Rule File

```python
# Use custom rule file
markdown = tomd(
    "https://example.com",
    rule_file="my-rules.yml"
)
```

**Priority:** `content_selector` parameter > rule file > auto-detection

## Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | str/Path | required | File path or URL to convert |
| `llm_enhance` | bool | False | Enable LLM enhancement |
| `language` | str | None | Target language for translation |
| `use_browser` | bool | False | Use headless browser (auto-fallback if needed) |
| `content_selector` | str | None | CSS selector for content extraction |
| `rule_file` | str/Path | None | Path to custom rule.yml file |
