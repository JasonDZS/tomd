"""LLM enhancement module for markdown content."""

import os
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


class LLMEnhancer:
    """Enhance markdown content using LLM."""

    def __init__(self):
        """Initialize the LLM enhancer with configuration from environment variables."""
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "8192"))

        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )

        logger.info(f"LLM enhancer initialized with model: {self.model}, max_tokens: {self.max_tokens}")
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    def _split_content(self, content: str, max_chunk_size: int = 3000) -> list[str]:
        """Split content into chunks by paragraphs."""
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para) + 2

            if current_size + para_size > max_chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def _enhance_chunk(
        self, chunk: str, language: Optional[str], system_prompt: str
    ) -> str:
        """Enhance a single chunk of content."""
        if language:
            user_prompt = (
                f"Please enhance and translate the following markdown content to {language}. "
                "Preserve all markdown formatting and structure. "
                "Make the content clear and professional.\n\n"
                f"{chunk}"
                "<enhanced_content>```markdown\n"
            )
        else:
            user_prompt = (
                "Please enhance the following markdown content. "
                "Preserve all markdown formatting and structure. "
                "Make the content more clear, concise, and well-organized.\n\n"
                f"{chunk}"
                "<enhanced_content>```markdown\n"
            )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=0.3,
        )

        enhanced_content = response.choices[0].message.content.strip().split("```</enhanced_content>")[0].replace("```markdown\n", "").strip()
        return enhanced_content

    def enhance(self, content: str, language: Optional[str] = None) -> str:
        """
        Enhance markdown content using LLM.

        Args:
            content: The markdown content to enhance
            language: Target language for translation (e.g., "Chinese", "English", "Japanese")
                     If None, content will be enhanced without translation

        Returns:
            Enhanced and optionally translated markdown content

        Raises:
            ValueError: If API key is not configured
            Exception: If LLM API call fails
        """
        logger.info(f"Enhancing content (length: {len(content)}, language: {language or 'None'})")

        system_prompt = (
            "You are a professional content editor and translator. "
            "Your task is to improve the quality of markdown content while preserving its structure. "
            "Keep all markdown formatting (headers, lists, links, code blocks, etc.) intact. "
            "Make the content more clear, concise, and well-organized."
            "You can clean up grammar, web action info (eg: 'loading', 'share'), improve phrasing, and enhance readability. "
            "You can remove paragraphs that do not add value to the main content. such as ads, unrelated links, or navigation instructions."
            "**IMPORTANT**: ALL ENHANCED CONTENT MUST BE MADE WITHOUT ADDITIONAL INFORMATION OR CONTEXT.\n"
            "<output_format>"
            "<enhanced_content>```markdown\n...enhanced markdown content...```</enhanced_content>"
            "</output_format>"
        )

        try:
            # Check if content needs to be split
            if len(content) > 3000:
                chunks = self._split_content(content)
                logger.info(f"Content split into {len(chunks)} chunks")
                enhanced_chunks = []
                for i, chunk in enumerate(chunks, 1):
                    logger.debug(f"Processing chunk {i}/{len(chunks)} (size: {len(chunk)})")
                    enhanced_chunk = self._enhance_chunk(chunk, language, system_prompt)
                    enhanced_chunks.append(enhanced_chunk)
                    logger.debug(f"Chunk {i}/{len(chunks)} processed")
                result = "\n\n".join(enhanced_chunks)
                logger.success(f"All chunks processed, final length: {len(result)}")
                return result
            else:
                logger.debug("Content size under threshold, processing as single chunk")
                result = self._enhance_chunk(content, language, system_prompt)
                logger.success(f"Enhancement completed, final length: {len(result)}")
                return result

        except Exception as e:
            logger.error(f"LLM enhancement failed: {str(e)}")
            raise Exception(f"LLM enhancement failed: {str(e)}") from e


def enhance_markdown(
    content: str, language: Optional[str] = None, enabled: bool = True
) -> str:
    """
    Convenience function to enhance markdown content.

    Args:
        content: The markdown content to enhance
        language: Target language for translation
        enabled: Whether to enable LLM enhancement

    Returns:
        Enhanced content if enabled, otherwise original content
    """
    if not enabled:
        return content

    enhancer = LLMEnhancer()
    return enhancer.enhance(content, language)
