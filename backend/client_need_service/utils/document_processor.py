"""
Document processing utilities for text extraction and normalization.
Handles PDF, text, and other document formats for data ingestion.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from io import BytesIO
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document text extraction and normalization."""

    @staticmethod
    def extract_text_from_pdf(
        pdf_content: bytes,
        extract_metadata: bool = True
    ) -> Tuple[str, Optional[Dict]]:
        """
        Extract text from PDF content.

        Args:
            pdf_content: PDF file content as bytes
            extract_metadata: Whether to extract PDF metadata

        Returns:
            Tuple of (extracted_text, metadata_dict)

        Raises:
            ValueError: If PDF is invalid or cannot be processed
        """
        try:
            pdf_file = BytesIO(pdf_content)
            reader = PdfReader(pdf_file)

            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue

            extracted_text = "\n\n".join(text_parts)

            # Extract metadata if requested
            metadata = None
            if extract_metadata:
                metadata = {
                    "num_pages": len(reader.pages),
                    "pdf_metadata": {}
                }

                if reader.metadata:
                    metadata["pdf_metadata"] = {
                        "title": reader.metadata.get("/Title"),
                        "author": reader.metadata.get("/Author"),
                        "subject": reader.metadata.get("/Subject"),
                        "creator": reader.metadata.get("/Creator"),
                        "producer": reader.metadata.get("/Producer"),
                        "creation_date": str(reader.metadata.get("/CreationDate")),
                    }

            logger.info(f"Extracted {len(extracted_text)} chars from {len(reader.pages)} pages")

            return extracted_text, metadata

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise ValueError(f"Invalid PDF or extraction failed: {str(e)}")

    @staticmethod
    def normalize_text(
        text: str,
        remove_extra_whitespace: bool = True,
        normalize_line_breaks: bool = True
    ) -> str:
        """
        Normalize text content.

        Args:
            text: Raw text to normalize
            remove_extra_whitespace: Remove extra spaces and tabs
            normalize_line_breaks: Normalize line break patterns

        Returns:
            Normalized text
        """
        if not text:
            return ""

        normalized = text

        # Normalize line breaks
        if normalize_line_breaks:
            normalized = normalized.replace('\r\n', '\n').replace('\r', '\n')

        # Remove extra whitespace
        if remove_extra_whitespace:
            # Replace multiple spaces with single space
            normalized = re.sub(r'[ \t]+', ' ', normalized)
            # Remove trailing whitespace from each line
            normalized = '\n'.join(line.rstrip() for line in normalized.split('\n'))
            # Remove multiple consecutive blank lines
            normalized = re.sub(r'\n{3,}', '\n\n', normalized)

        return normalized.strip()

    @staticmethod
    def extract_sections(
        text: str,
        section_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Extract sections from text based on heading patterns.

        Args:
            text: Text to extract sections from
            section_patterns: Regex patterns for section headings
                            (default: common heading patterns)

        Returns:
            List of {title, content} dictionaries
        """
        if not text:
            return []

        # Default patterns for common section headings
        if section_patterns is None:
            section_patterns = [
                r'^#{1,6}\s+(.+)$',  # Markdown headers
                r'^([A-Z][A-Za-z\s]+):$',  # Title Case Header:
                r'^([A-Z\s]+)$',  # ALL CAPS HEADER
                r'^\d+\.\s+([A-Z].+)$',  # 1. Numbered Header
            ]

        sections = []
        current_section = {"title": "Introduction", "content": ""}

        lines = text.split('\n')

        for line in lines:
            is_header = False

            # Check if line matches any section pattern
            for pattern in section_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    # Save current section if it has content
                    if current_section["content"].strip():
                        sections.append(current_section)

                    # Start new section
                    current_section = {
                        "title": match.group(1).strip(),
                        "content": ""
                    }
                    is_header = True
                    break

            # Add line to current section content
            if not is_header:
                current_section["content"] += line + "\n"

        # Add the last section
        if current_section["content"].strip():
            sections.append(current_section)

        # Clean up section content
        for section in sections:
            section["content"] = section["content"].strip()

        logger.info(f"Extracted {len(sections)} sections from text")

        return sections

    @staticmethod
    def calculate_word_count(text: str) -> int:
        """
        Calculate word count in text.

        Args:
            text: Text to count words in

        Returns:
            Number of words
        """
        if not text:
            return 0

        # Split on whitespace and count non-empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words)

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Simple language detection (basic heuristic).

        Args:
            text: Text to detect language from

        Returns:
            Language code (e.g., 'en', 'es', 'fr')

        Note:
            This is a very basic implementation.
            For production, use a library like langdetect or Azure Text Analytics.
        """
        if not text:
            return "unknown"

        # Very simple heuristic - just default to English for now
        # In production, you would use a proper language detection library
        return "en"

    @classmethod
    def process_document(
        cls,
        content: bytes,
        content_type: str,
        extract_sections: bool = True
    ) -> Dict:
        """
        Main document processing pipeline.

        Args:
            content: Document content as bytes
            content_type: MIME type (e.g., 'application/pdf', 'text/plain')
            extract_sections: Whether to extract sections

        Returns:
            Dictionary with normalized content and metadata

        Raises:
            ValueError: If document type is unsupported or processing fails
        """
        try:
            # Extract text based on content type
            if content_type == 'application/pdf':
                raw_text, pdf_metadata = cls.extract_text_from_pdf(content)
                extra_metadata = pdf_metadata or {}
            elif content_type.startswith('text/'):
                raw_text = content.decode('utf-8')
                extra_metadata = {}
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            # Normalize text
            normalized_text = cls.normalize_text(raw_text)

            # Extract sections if requested
            sections = None
            if extract_sections:
                sections = cls.extract_sections(normalized_text)

            # Calculate metadata
            word_count = cls.calculate_word_count(normalized_text)
            language = cls.detect_language(normalized_text)

            result = {
                "text": normalized_text,
                "sections": sections,
                "word_count": word_count,
                "language": language,
                **extra_metadata
            }

            logger.info(f"Processed document: {word_count} words, {len(sections) if sections else 0} sections")

            return result

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
