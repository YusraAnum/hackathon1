"""
Content Chunking Service

This service handles the chunking of textbook content into smaller pieces
suitable for embedding and storage in the vector database.
"""

from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a chunk of content with metadata."""
    id: str
    content: str
    chapter_id: str
    chapter_title: str
    section: str
    order: int
    metadata: Dict[str, Any]

class ContentChunkingService:
    def __init__(self, max_chunk_size: int = 512, overlap_size: int = 50):
        """
        Initialize the content chunking service.

        Args:
            max_chunk_size: Maximum number of characters per chunk
            overlap_size: Number of characters to overlap between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def chunk_textbook_content(self, chapter_id: str, title: str, content: str, order: int = 0) -> List[ContentChunk]:
        """
        Chunk the textbook content into smaller pieces for embedding.

        Args:
            chapter_id: Unique identifier for the chapter
            title: Chapter title
            content: Full chapter content
            order: Chapter order number

        Returns:
            List of content chunks with metadata
        """
        try:
            # Split content by paragraphs first
            paragraphs = self._split_into_paragraphs(content)

            chunks = []
            chunk_id = 0

            for paragraph in paragraphs:
                # If paragraph is smaller than max chunk size, use it as is
                if len(paragraph) <= self.max_chunk_size:
                    chunk = ContentChunk(
                        id=f"{chapter_id}_chunk_{chunk_id}",
                        content=paragraph,
                        chapter_id=chapter_id,
                        chapter_title=title,
                        section=self._extract_section_title(paragraph, title),
                        order=order,
                        metadata={
                            "type": "paragraph",
                            "original_length": len(paragraph)
                        }
                    )
                    chunks.append(chunk)
                    chunk_id += 1
                else:
                    # If paragraph is too long, split it further
                    sub_chunks = self._chunk_large_paragraph(paragraph)
                    for sub_chunk in sub_chunks:
                        chunk = ContentChunk(
                            id=f"{chapter_id}_chunk_{chunk_id}",
                            content=sub_chunk,
                            chapter_id=chapter_id,
                            chapter_title=title,
                            section=self._extract_section_title(sub_chunk, title),
                            order=order,
                            metadata={
                                "type": "sub_chunk",
                                "original_length": len(sub_chunk)
                            }
                        )
                        chunks.append(chunk)
                        chunk_id += 1

            # Apply overlap between chunks if needed
            if self.overlap_size > 0:
                chunks = self._apply_overlap(chunks)

            logger.info(f"Chunked chapter {chapter_id} into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error chunking content for chapter {chapter_id}: {e}")
            # Return a single chunk if chunking fails
            return [
                ContentChunk(
                    id=f"{chapter_id}_chunk_0",
                    content=content,
                    chapter_id=chapter_id,
                    chapter_title=title,
                    section=title,
                    order=order,
                    metadata={
                        "type": "fallback",
                        "original_length": len(content)
                    }
                )
            ]

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """Split content into paragraphs based on double newlines."""
        # Split by double newlines first
        paragraphs = content.split('\n\n')

        # Clean up and filter empty paragraphs
        cleaned_paragraphs = []
        for paragraph in paragraphs:
            cleaned = paragraph.strip()
            if cleaned:
                cleaned_paragraphs.append(cleaned)

        return cleaned_paragraphs

    def _chunk_large_paragraph(self, paragraph: str) -> List[str]:
        """Split a large paragraph into smaller chunks."""
        chunks = []
        start = 0

        while start < len(paragraph):
            # Find the end of the chunk
            end = start + self.max_chunk_size

            # If we're at the end, take the remaining text
            if end >= len(paragraph):
                chunks.append(paragraph[start:])
                break

            # Try to break at sentence boundary if possible
            sentence_end = self._find_sentence_break(paragraph, start, end)

            if sentence_end > start:
                # Found a sentence break
                chunk = paragraph[start:sentence_end].strip()
                if chunk:
                    chunks.append(chunk)
                start = sentence_end
            else:
                # No sentence break found, break at word boundary
                word_end = self._find_word_break(paragraph, start, end)

                if word_end > start:
                    chunk = paragraph[start:word_end].strip()
                    if chunk:
                        chunks.append(chunk)
                    start = word_end
                else:
                    # No word break found, break at character boundary
                    chunk = paragraph[start:end].strip()
                    if chunk:
                        chunks.append(chunk)
                    start = end

        return chunks

    def _find_sentence_break(self, text: str, start: int, end: int) -> int:
        """Find the last sentence break within the chunk range."""
        # Look for sentence-ending punctuation followed by space or end of text
        for i in range(min(end, len(text)) - 1, start, -1):
            if text[i] in '.!?' and (i + 1 >= len(text) or text[i + 1].isspace()):
                # Check if it's not part of an abbreviation (simple heuristic)
                if i > 0 and text[i-1].isalpha() and (i < 2 or text[i-2].isupper()):
                    continue  # Likely part of an abbreviation
                return i + 1

        return -1  # No sentence break found

    def _find_word_break(self, text: str, start: int, end: int) -> int:
        """Find the last word break within the chunk range."""
        for i in range(min(end, len(text)) - 1, start, -1):
            if text[i].isspace():
                return i

        return end  # No word break found, return the end position

    def _extract_section_title(self, content: str, chapter_title: str) -> str:
        """Extract section title from content if available, otherwise return chapter title."""
        # Look for potential section headers in the content
        lines = content.split('\n')[:5]  # Check first 5 lines for headers

        for line in lines:
            # Check for markdown-style headers (## Section Title)
            if line.strip().startswith('##'):
                return line.strip()[2:].strip()  # Remove '##' and extra spaces
            # Check for other header patterns
            elif line.strip().endswith(':') and len(line.strip()) < 100:
                return line.strip()[:-1].strip()  # Remove ':' and extra spaces

        return chapter_title

    def _apply_overlap(self, chunks: List[ContentChunk]) -> List[ContentChunk]:
        """Apply overlap between consecutive chunks."""
        if len(chunks) <= 1:
            return chunks

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            new_content = chunk.content

            # Add overlap from the previous chunk if it exists
            if i > 0 and len(chunk.content) >= self.overlap_size:
                prev_chunk_end = chunks[i-1].content[-self.overlap_size:]
                new_content = prev_chunk_end + " " + chunk.content

            # Add overlap from the next chunk if it exists
            if i < len(chunks) - 1 and len(chunk.content) >= self.overlap_size:
                next_chunk_start = chunks[i+1].content[:self.overlap_size]
                new_content = chunk.content + " " + next_chunk_start

            overlapped_chunk = ContentChunk(
                id=chunk.id,
                content=new_content,
                chapter_id=chunk.chapter_id,
                chapter_title=chunk.chapter_title,
                section=chunk.section,
                order=chunk.order,
                metadata=chunk.metadata
            )

            overlapped_chunks.append(overlapped_chunk)

        return overlapped_chunks

    def process_chapter(self, chapter_data: Dict[str, Any]) -> List[ContentChunk]:
        """
        Process a single chapter and return its chunks.

        Args:
            chapter_data: Dictionary containing chapter information

        Returns:
            List of content chunks
        """
        chapter_id = chapter_data.get('id', 'unknown')
        title = chapter_data.get('title', 'Unknown Chapter')
        content = chapter_data.get('content', '')
        order = chapter_data.get('order', 0)

        return self.chunk_textbook_content(chapter_id, title, content, order)

# Global instance of the content chunking service
content_chunking_service = ContentChunkingService()