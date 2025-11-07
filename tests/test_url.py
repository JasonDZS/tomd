"""Tests for URL converter."""

import pytest
import requests
from unittest.mock import Mock, patch

from tomd import tomd


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_with_url(mock_get):
    """Test converting a URL to Markdown."""
    # Mock the response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
    <body>
        <article>
            <h1>Test Article</h1>
            <p>This is a test article from a website.</p>
            <ul>
                <li>Point 1</li>
                <li>Point 2</li>
            </ul>
        </article>
    </body>
    </html>
    """
    mock_get.return_value = mock_response

    url = "https://example.com/article"
    result = tomd(url)

    # Check that the URL was called
    mock_get.assert_called_once()

    # Check that key elements are converted
    assert "Source: https://example.com/article" in result
    assert "# Test Article" in result
    assert "test article" in result
    assert "Point 1" in result
    assert "Point 2" in result


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_with_https_url(mock_get):
    """Test that https URLs are recognized."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>HTTPS Test</h1></body></html>"
    mock_get.return_value = mock_response

    url = "https://secure.example.com/page"
    result = tomd(url)

    assert "Source: https://secure.example.com/page" in result
    assert "# HTTPS Test" in result


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_with_http_url(mock_get):
    """Test that http URLs are recognized."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>HTTP Test</h1></body></html>"
    mock_get.return_value = mock_response

    url = "http://example.com/page"
    result = tomd(url)

    assert "Source: http://example.com/page" in result
    assert "# HTTP Test" in result


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_url_removes_scripts_and_styles(mock_get):
    """Test that script and style tags are removed."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
    <head>
        <style>body { color: red; }</style>
    </head>
    <body>
        <script>console.log('test');</script>
        <h1>Clean Content</h1>
        <p>This should appear.</p>
    </body>
    </html>
    """
    mock_get.return_value = mock_response

    url = "https://example.com/page"
    result = tomd(url)

    # Script and style content should not appear
    assert "console.log" not in result
    assert "color: red" not in result

    # Main content should appear
    assert "# Clean Content" in result
    assert "This should appear" in result


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_url_with_main_tag(mock_get):
    """Test that main content area is extracted."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
    <body>
        <nav>Navigation</nav>
        <main>
            <h1>Main Content</h1>
            <p>This is the main content.</p>
        </main>
        <footer>Footer content</footer>
    </body>
    </html>
    """
    mock_get.return_value = mock_response

    url = "https://example.com/page"
    result = tomd(url)

    # Main content should appear
    assert "# Main Content" in result
    assert "main content" in result


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_url_request_error(mock_get):
    """Test that request errors are handled."""
    mock_get.side_effect = requests.RequestException("Connection error")

    url = "https://example.com/page"

    with pytest.raises(requests.RequestException):
        tomd(url)


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_url_404_error(mock_get):
    """Test that 404 errors are handled."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    url = "https://example.com/notfound"

    with pytest.raises(requests.HTTPError):
        tomd(url)


def test_tomd_distinguishes_url_from_file():
    """Test that URLs are distinguished from file paths."""
    # This should try to process as URL (will fail without mocking, but that's ok)
    url = "https://example.com/page"

    # Should not raise FileNotFoundError (which would indicate it's treating it as a file)
    with pytest.raises(requests.RequestException):
        tomd(url)


@patch("tomd.converters.url_converter.requests.get")
def test_tomd_url_with_complex_html(mock_get):
    """Test converting a complex HTML page."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
    <body>
        <article>
            <h1>Blog Post Title</h1>
            <p>Introduction paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
            <h2>Section 1</h2>
            <p>Section content with a <a href="https://example.com">link</a>.</p>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
            </ul>
            <h2>Section 2</h2>
            <p>More content here.</p>
        </article>
    </body>
    </html>
    """
    mock_get.return_value = mock_response

    url = "https://example.com/blog/post"
    result = tomd(url)

    # Check structure is preserved
    assert "# Blog Post Title" in result
    assert "## Section 1" in result
    assert "## Section 2" in result
    assert "**bold**" in result
    # html2text uses underscore for italic
    assert "_italic_" in result or "*italic*" in result
    assert "[link]" in result
    assert "List item 1" in result
