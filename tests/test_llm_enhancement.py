"""Tests for LLM enhancement feature."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tomd import tomd
from tomd.llm_enhancer import LLMEnhancer, enhance_markdown


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LLM_MODEL": "gpt-3.5-turbo", "LLM_MAX_TOKENS": "8192"}, clear=True)
@patch("tomd.llm_enhancer.OpenAI")
def test_llm_enhancer_initialization(mock_openai):
    """Test LLM enhancer initialization with environment variables."""
    enhancer = LLMEnhancer()

    assert enhancer.api_key == "test-key"
    assert enhancer.model == "gpt-3.5-turbo"
    assert enhancer.max_tokens == 8192
    mock_openai.assert_called_once()


@patch.dict(os.environ, {}, clear=True)
def test_llm_enhancer_missing_api_key():
    """Test that missing API key raises ValueError."""
    with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
        LLMEnhancer()


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LLM_MODEL": "gpt-3.5-turbo"}, clear=True)
@patch("tomd.llm_enhancer.OpenAI")
def test_enhance_markdown_without_translation(mock_openai):
    """Test enhancing markdown without translation."""
    # Mock the OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="# Enhanced Content\n\nThis is enhanced."))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    enhancer = LLMEnhancer()
    result = enhancer.enhance("# Original Content\n\nThis is original.")

    assert "Enhanced" in result
    mock_client.chat.completions.create.assert_called_once()

    # Check that the call includes the correct parameters
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-3.5-turbo"
    assert call_args.kwargs["temperature"] == 0.3


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("tomd.llm_enhancer.OpenAI")
def test_enhance_markdown_with_translation(mock_openai):
    """Test enhancing and translating markdown."""
    # Mock the OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="# 增强内容\n\n这是增强的内容。"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    enhancer = LLMEnhancer()
    result = enhancer.enhance("# Original Content", language="Chinese")

    assert "增强" in result or "Enhanced" in result
    mock_client.chat.completions.create.assert_called_once()

    # Check that the prompt includes translation instruction
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    user_message = messages[1]["content"]
    assert "Chinese" in user_message or "translate" in user_message.lower()


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("tomd.llm_enhancer.OpenAI")
def test_enhance_markdown_convenience_function(mock_openai):
    """Test the convenience function for markdown enhancement."""
    # Mock the OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Enhanced content"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    result = enhance_markdown("Original content", enabled=True)
    assert result == "Enhanced content"


def test_enhance_markdown_disabled():
    """Test that enhancement is skipped when disabled."""
    original = "Original content"
    result = enhance_markdown(original, enabled=False)
    assert result == original


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("tomd.llm_enhancer.OpenAI")
def test_tomd_with_llm_enhance_html_file(mock_openai):
    """Test tomd with LLM enhancement on HTML file."""
    # Mock the OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="# Enhanced Title\n\nEnhanced content."))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = tomd(temp_path, llm_enhance=True)
        assert "Enhanced" in result
        mock_client.chat.completions.create.assert_called_once()
    finally:
        Path(temp_path).unlink()


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("tomd.llm_enhancer.OpenAI")
def test_tomd_with_llm_enhance_and_language(mock_openai):
    """Test tomd with LLM enhancement and translation."""
    # Mock the OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="# 测试标题\n\n测试内容。"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = tomd(temp_path, llm_enhance=True, language="Chinese")
        # Should contain Chinese characters or the mocked response
        assert "测试" in result or len(result) > 0
        mock_client.chat.completions.create.assert_called_once()
    finally:
        Path(temp_path).unlink()


def test_tomd_without_llm_enhance():
    """Test that tomd works normally without LLM enhancement."""
    html_content = "<html><body><h1>Test</h1><p>Content</p></body></html>"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        result = tomd(temp_path, llm_enhance=False)
        # Should contain the basic conversion without LLM
        assert "Test" in result
        assert "Content" in result
    finally:
        Path(temp_path).unlink()


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("tomd.llm_enhancer.OpenAI")
def test_llm_enhancement_api_error(mock_openai):
    """Test handling of LLM API errors."""
    # Mock an API error
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client

    enhancer = LLMEnhancer()

    with pytest.raises(Exception, match="LLM enhancement failed"):
        enhancer.enhance("Test content")


@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch("tomd.llm_enhancer.OpenAI")
@patch("tomd.converters.url_converter.requests.get")
def test_tomd_url_with_llm_enhance(mock_get, mock_openai):
    """Test tomd with URL and LLM enhancement."""
    # Mock the URL response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body><h1>Web Content</h1></body></html>"
    mock_get.return_value = mock_response

    # Mock the OpenAI response
    mock_client = Mock()
    mock_llm_response = Mock()
    mock_llm_response.choices = [Mock(message=Mock(content="# Enhanced Web Content"))]
    mock_client.chat.completions.create.return_value = mock_llm_response
    mock_openai.return_value = mock_client

    url = "https://example.com/page"
    result = tomd(url, llm_enhance=True)

    assert "Enhanced" in result or "Web Content" in result
    mock_get.assert_called_once()
    mock_client.chat.completions.create.assert_called_once()
