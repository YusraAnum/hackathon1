import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.textbook_content import Textbook, Chapter
from src.services.database_service import get_db
from src.utils.logging import get_logger
from src.utils.config import settings
from src.services.cache_service import cache_service
from src.services.translation_service import translation_service
from src.services.personalization_service import personalization_service


logger = get_logger(__name__)


class ContentService:
    def __init__(self):
        self.content_dir = Path("docs/textbook")
        self._ensure_content_dir_exists()

    def _ensure_content_dir_exists(self):
        """Ensure the content directory exists"""
        if not self.content_dir.exists():
            logger.warning(f"Content directory {self.content_dir} does not exist, creating it")
            self.content_dir.mkdir(parents=True, exist_ok=True)

    def load_chapter_from_file(self, chapter_id: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        """Load a chapter from markdown file with optional language-specific version"""
        # First, try to find a language-specific version of the chapter
        language_file_pattern = f"*-{chapter_id}.{language}.md"
        language_files = list(self.content_dir.glob(language_file_pattern))

        if not language_files and language != 'en':
            # If no language-specific file found, try to find a language-specific version with the original pattern
            for file_path in self.content_dir.glob("*.md"):
                if f"{chapter_id}.{language}" in file_path.stem:
                    language_files = [file_path]
                    break

        # If we found a language-specific file, use it
        if language_files:
            file_path = language_files[0]
        else:
            # Otherwise, look for the default file
            default_file = None
            for file_path in self.content_dir.glob("*.md"):
                if chapter_id.replace("-", "_") in file_path.stem.replace("-", "_"):
                    # Make sure this isn't a language-specific file (doesn't have a language code before .md)
                    if not any(file_path.stem.endswith(f".{lang}") for lang in ['ur', 'es', 'fr', 'de', 'zh']):
                        default_file = file_path
                        break

            if default_file:
                file_path = default_file
            else:
                return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter and content
            lines = content.split('\n')
            frontmatter = {}
            content_start = 0

            # Look for frontmatter
            if lines and lines[0].strip() == '---':
                content_start = 1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        content_start = i + 1
                        frontmatter_content = '\n'.join(lines[1:i])
                        try:
                            import yaml
                            frontmatter = yaml.safe_load(frontmatter_content)
                            if frontmatter is None:
                                frontmatter = {}
                        except:
                            # If YAML parsing fails, just skip frontmatter
                            frontmatter = {}
                        break

            # Get the actual content (after frontmatter if present)
            actual_content = '\n'.join(lines[content_start:])

            # Convert markdown to HTML for display
            html_content = markdown.markdown(actual_content, extensions=['fenced_code', 'codehilite'])

            # Calculate word count and reading time
            word_count = len(actual_content.split())
            reading_time = f"{max(1, word_count // 200)} min"

            # Use filename or frontmatter title
            title = frontmatter.get('title', chapter_id.replace('-', ' ').title())

            return {
                'id': chapter_id,
                'title': title,
                'content': html_content,
                'raw_content': actual_content,
                'order': self._extract_order_from_filename(file_path.name),
                'word_count': word_count,
                'reading_time': reading_time,
                'created_at': "2025-12-01T00:00:00Z",
                'updated_at': "2025-12-01T00:00:00Z",
                'language': language
            }
        except Exception as e:
            logger.error(f"Error loading chapter {chapter_id} from file {file_path}: {e}")
            return None

    def _extract_order_from_filename(self, filename: str) -> int:
        """Extract order number from filename like '01-introduction-to-physical-ai.md'"""
        try:
            prefix = filename.split('-')[0]
            return int(prefix)
        except (ValueError, IndexError):
            return 999  # Default high number if can't parse

    def get_all_chapters(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get all chapters with pagination and caching (default to English)"""
        return self.get_all_chapters_with_language(limit, offset, 'en')

    def get_all_chapters_with_language(self, limit: int = 10, offset: int = 0, language: str = 'en') -> Dict[str, Any]:
        """Get all chapters with pagination, caching and specified language"""
        try:
            # Create cache key based on parameters including language
            cache_key = f"chapters:lang={language}:limit={limit}:offset={offset}"
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for all chapters in language {language} with limit={limit}, offset={offset}")
                return cached_result

            # First try to get from database - for now only English from DB
            chapters_from_db = None
            if language == 'en':
                chapters_from_db = self._get_chapters_from_db(limit, offset)

            if chapters_from_db:
                # Cache the result
                cache_service.set(cache_key, chapters_from_db, ttl=900)  # 15 minutes
                return chapters_from_db

            # If no database chapters or non-English, try to load from files
            chapters = []
            for file_path in sorted(self.content_dir.glob("*.md")):
                # Skip language-specific files when loading default language
                if language == 'en' and any(file_path.stem.endswith(f".{lang}") for lang in ['ur', 'es', 'fr', 'de', 'zh']):
                    continue

                chapter_id = self._extract_chapter_id_from_filename(file_path.name)

                # For non-English, try to load language-specific version
                chapter_data = self.load_chapter_from_file(chapter_id, language)
                if chapter_data:
                    chapters.append(chapter_data)

            # Sort by order
            chapters.sort(key=lambda x: x['order'])

            # Apply pagination
            paginated_chapters = chapters[offset:offset + limit]
            total = len(chapters)

            result = {
                'chapters': paginated_chapters,
                'total': total,
                'limit': limit,
                'offset': offset
            }

            # Cache the result
            cache_service.set(cache_key, result, ttl=900)  # 15 minutes
            return result
        except Exception as e:
            logger.error(f"Error getting all chapters in language {language}: {e}")
            return {
                'chapters': [],
                'total': 0,
                'limit': limit,
                'offset': offset
            }

    def _extract_chapter_id_from_filename(self, filename: str) -> str:
        """Extract chapter ID from filename"""
        name_part = filename.replace('.md', '')
        # Remove order prefix like '01-' from '01-introduction-to-physical-ai.md'
        parts = name_part.split('-', 1)
        if len(parts) > 1 and parts[0].isdigit():
            return parts[1]
        return name_part

    def get_chapter_by_id(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chapter by ID with caching (default to English)"""
        return self.get_chapter_by_id_with_language(chapter_id, 'en')

    def get_chapter_by_id_with_language(self, chapter_id: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        """Get a specific chapter by ID with specified language and caching"""
        try:
            # Check cache first (include language in cache key)
            cache_key = f"chapter:{chapter_id}:lang:{language}"
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for chapter {chapter_id} in language {language}")
                return cached_result

            # First try database - if we need to extend this to support multiple languages in DB,
            # we'd need to modify the database schema to store language-specific content
            chapter_from_db = self._get_chapter_from_db(chapter_id)
            if chapter_from_db and language == 'en':  # For now, only serve DB content for English
                # Cache the result
                cache_service.set(cache_key, chapter_from_db, ttl=600)  # 10 minutes
                return chapter_from_db

            # If not in database or non-English, try file system
            result = self.load_chapter_from_file(chapter_id, language)
            if result:
                # Cache the result
                cache_service.set(cache_key, result, ttl=600)  # 10 minutes

            return result
        except Exception as e:
            logger.error(f"Error getting chapter {chapter_id} in language {language}: {e}")
            return None

    def _get_chapters_from_db(self, limit: int, offset: int) -> Optional[Dict[str, Any]]:
        """Get chapters from database if available - optimized query"""
        try:
            from src.services.database_service import SessionLocal
            db = SessionLocal()

            # Check if we have chapters in the database
            total = db.query(Chapter).count()
            if total == 0:
                return None

            # Use specific columns to reduce data transfer when content not needed
            chapters_db = db.query(Chapter).order_by(Chapter.order).offset(offset).limit(limit).all()

            chapters = []
            for ch in chapters_db:
                chapters.append({
                    'id': str(ch.id),
                    'title': ch.title,
                    'content': ch.content,  # Consider removing this if not needed for listing
                    'order': ch.order,
                    'word_count': ch.word_count,
                    'reading_time': ch.reading_time,
                    'created_at': ch.created_at.isoformat() if ch.created_at else None,
                    'updated_at': ch.updated_at.isoformat() if ch.updated_at else None
                })

            return {
                'chapters': chapters,
                'total': total,
                'limit': limit,
                'offset': offset
            }
        except Exception as e:
            logger.warning(f"Database query failed: {e}, falling back to file system")
            return None
        finally:
            db.close()

    def _get_chapter_from_db(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chapter from database"""
        try:
            from src.services.database_service import SessionLocal
            db = SessionLocal()

            chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if chapter:
                return {
                    'id': str(chapter.id),
                    'title': chapter.title,
                    'content': chapter.content,
                    'order': chapter.order,
                    'word_count': chapter.word_count,
                    'reading_time': chapter.reading_time,
                    'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
                    'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None
                }
        except Exception as e:
            logger.warning(f"Database query failed: {e}")
        finally:
            db.close()

        return None

    def get_chapter_toc(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        """Get table of contents for a specific chapter with caching"""
        # Check cache first
        cache_key = f"chapter_toc:{chapter_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for TOC of chapter {chapter_id}")
            return cached_result

        chapter = self.get_chapter_by_id(chapter_id)
        if not chapter or not chapter.get('raw_content'):
            return None

        try:
            # Parse raw markdown content to extract headings with proper IDs
            raw_content = chapter['raw_content']

            # Extract headings from markdown content with proper anchor IDs
            lines = raw_content.split('\n')
            sections = []

            for i, line in enumerate(lines):
                # Check for markdown headings (e.g., ## Heading, ### Heading, etc.)
                if line.strip().startswith(('# ', '## ', '### ', '#### ', '##### ', '###### ')):
                    # Count the number of # symbols to determine the level
                    level = 0
                    for char in line:
                        if char == '#':
                            level += 1
                        else:
                            break

                    # Extract the heading text (remove leading # and whitespace)
                    heading_text = line.lstrip('# ').strip()

                    # Create a URL-friendly ID from the heading text
                    section_id = self._create_section_id(heading_text)

                    sections.append({
                        'id': section_id,
                        'title': heading_text,
                        'level': level,
                        'order': len(sections) + 1
                    })

            result = {
                'chapterId': chapter_id,
                'title': chapter.get('title', chapter_id),
                'sections': sections
            }

            # Cache the result
            cache_service.set(cache_key, result, ttl=1800)  # 30 minutes (TOC changes less frequently)
            return result
        except Exception as e:
            logger.error(f"Error generating TOC for chapter {chapter_id}: {e}")
            return {
                'chapterId': chapter_id,
                'title': chapter.get('title', chapter_id),
                'sections': []
            }

    def _create_section_id(self, title: str) -> str:
        """Create a URL-friendly ID from a section title"""
        # Convert to lowercase and replace spaces with hyphens
        import re
        id_str = title.lower().replace(' ', '-').replace('_', '-')
        # Remove special characters except hyphens
        id_str = re.sub(r'[^a-z0-9-]', '', id_str)
        # Remove multiple consecutive hyphens
        id_str = re.sub(r'-+', '-', id_str)
        # Remove leading/trailing hyphens
        id_str = id_str.strip('-')
        return id_str

    def sync_content_to_db(self):
        """Sync content from files to database and invalidate cache"""
        try:
            from src.services.database_service import SessionLocal
            db = SessionLocal()

            # Create a default textbook if it doesn't exist
            textbook = db.query(Textbook).first()
            if not textbook:
                textbook = Textbook(title="AI-Native Textbook", version="1.0")
                db.add(textbook)
                db.commit()
                db.refresh(textbook)

            # Load all chapters from files
            updated_chapters = []
            for file_path in self.content_dir.glob("*.md"):
                chapter_id = self._extract_chapter_id_from_filename(file_path.name)
                chapter_data = self.load_chapter_from_file(chapter_id)

                if chapter_data:
                    # Check if chapter already exists
                    existing_chapter = db.query(Chapter).filter(Chapter.id == chapter_data['id']).first()

                    if existing_chapter:
                        # Update existing chapter
                        existing_chapter.title = chapter_data['title']
                        existing_chapter.content = chapter_data['content']
                        existing_chapter.order = chapter_data['order']
                        existing_chapter.word_count = chapter_data['word_count']
                        existing_chapter.reading_time = chapter_data['reading_time']
                    else:
                        # Create new chapter
                        chapter = Chapter(
                            id=chapter_data['id'],
                            textbook_id=textbook.id,
                            title=chapter_data['title'],
                            content=chapter_data['content'],
                            order=chapter_data['order'],
                            word_count=chapter_data['word_count'],
                            reading_time=chapter_data['reading_time']
                        )
                        db.add(chapter)

                    updated_chapters.append(chapter_id)

            db.commit()

            # Invalidate cache for updated chapters
            for chapter_id in updated_chapters:
                cache_service.delete(f"chapter:{chapter_id}")
                cache_service.delete(f"chapter_toc:{chapter_id}")

            # Also invalidate the chapters list cache
            cache_service.invalidate_pattern("chapters:")

            logger.info(f"Synced {len(updated_chapters)} chapters to database and invalidated related cache entries")
        except Exception as e:
            logger.error(f"Error syncing content to database: {e}")
            db.rollback()
        finally:
            db.close()

    def get_chapter_by_id_with_options(self, chapter_id: str, language: Optional[str] = None,
                                     personalization_enabled: bool = False, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific chapter by ID with optional translation and personalization

        Args:
            chapter_id: ID of the chapter to retrieve
            language: Target language for translation (e.g., 'ur' for Urdu)
            personalization_enabled: Whether to apply personalization
            session_id: User session ID for personalization preferences

        Returns:
            Chapter data with optional translation/personalization applied
        """
        try:
            # Use the specified language, or default to English
            target_language = language if language else 'en'

            # Get the chapter in the requested language
            chapter_data = self.get_chapter_by_id_with_language(chapter_id, target_language)
            if not chapter_data:
                return None

            # Apply personalization if requested (translation is handled by loading the right file)
            if personalization_enabled and session_id:
                # Get user preferences
                user_preferences = personalization_service.get_user_preferences(session_id)

                # Apply personalization to content
                if chapter_data.get('content'):
                    personalized_content = personalization_service.personalize_content(
                        chapter_data['content'],
                        user_preferences
                    )
                    chapter_data['content'] = personalized_content

            return chapter_data
        except Exception as e:
            logger.error(f"Error getting chapter {chapter_id} with options: {e}")
            return None

    def get_all_chapters_with_options(self, limit: int = 10, offset: int = 0,
                                    language: Optional[str] = None,
                                    personalization_enabled: bool = False,
                                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all chapters with optional translation and personalization

        Args:
            limit: Number of chapters to return
            offset: Offset for pagination
            language: Target language for translation
            personalization_enabled: Whether to apply personalization
            session_id: User session ID for personalization preferences

        Returns:
            Dictionary with chapters and metadata
        """
        try:
            # Use the specified language, or default to English
            target_language = language if language else 'en'

            # Get the chapters in the requested language
            chapters_data = self.get_all_chapters_with_language(limit=limit, offset=offset, language=target_language)

            # Apply personalization to each chapter if requested (translation is handled by loading the right files)
            if personalization_enabled and session_id:
                for chapter in chapters_data['chapters']:
                    if chapter.get('content'):
                        # Apply personalization to content
                        user_preferences = personalization_service.get_user_preferences(session_id)
                        personalized_content = personalization_service.personalize_content(
                            chapter['content'],
                            user_preferences
                        )
                        chapter['content'] = personalized_content

            return chapters_data
        except Exception as e:
            logger.error(f"Error getting all chapters with options: {e}")
            return {
                'chapters': [],
                'total': 0,
                'limit': limit,
                'offset': offset
            }


# Global instance
content_service = ContentService()