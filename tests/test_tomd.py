"""Tests for the main tomd function."""

import tempfile
from pathlib import Path

import pytest

from tomd import tomd


def test_tomd_with_html_file():
    """Test converting an HTML file to Markdown."""
    html_content = """
    <html>
    <body>
        <h1>Hello World</h1>
        <p>This is a <strong>test</strong> paragraph.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = tomd(temp_path)

        # Check that key elements are converted
        assert "# Hello World" in result
        assert "**test**" in result
        assert "Item 1" in result
        assert "Item 2" in result
    finally:
        Path(temp_path).unlink()


def test_tomd_with_text_file():
    """Test converting a plain text file."""
    text_content = "This is plain text.\nWith multiple lines."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text_content)
        temp_path = f.name

    try:
        result = tomd(temp_path)
        assert result == text_content
    finally:
        Path(temp_path).unlink()


def test_tomd_with_markdown_file():
    """Test that markdown files pass through unchanged."""
    md_content = "# Title\n\nThis is **markdown**."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(md_content)
        temp_path = f.name

    try:
        result = tomd(temp_path)
        assert result == md_content
    finally:
        Path(temp_path).unlink()


def test_tomd_with_nonexistent_file():
    """Test that FileNotFoundError is raised for nonexistent files."""
    with pytest.raises(FileNotFoundError):
        tomd("/nonexistent/file.html")


def test_tomd_with_directory():
    """Test that ValueError is raised when path is a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ValueError, match="Path is not a file"):
            tomd(temp_dir)


def test_tomd_with_unsupported_format():
    """Test that ValueError is raised for unsupported file formats."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
        f.write("content")
        temp_path = f.name

    try:
        with pytest.raises(ValueError, match="Unsupported file format"):
            tomd(temp_path)
    finally:
        Path(temp_path).unlink()


def test_tomd_with_path_object():
    """Test that tomd accepts Path objects."""
    text_content = "Test content"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text_content)
        temp_path = Path(f.name)

    try:
        result = tomd(temp_path)
        assert result == text_content
    finally:
        temp_path.unlink()
