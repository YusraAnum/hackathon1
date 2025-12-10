from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from src.services.content_service import content_service
from src.utils.cache_decorator import cached_endpoint

router = APIRouter()

# Pydantic models for request/response
class Chapter(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    order: int
    wordCount: Optional[int] = None
    readingTime: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class ChapterListResponse(BaseModel):
    chapters: List[Chapter]
    total: int
    limit: int
    offset: int

class TableOfContents(BaseModel):
    chapterId: str
    title: str
    sections: List[dict]

@router.get("/chapters", response_model=ChapterListResponse)
@cached_endpoint(ttl=900)  # Cache for 15 minutes
async def get_chapters(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Retrieve all textbook chapters with metadata.
    """
    chapters_data = content_service.get_all_chapters(limit=limit, offset=offset)

    # Convert to response format
    chapters = []
    for ch in chapters_data['chapters']:
        chapter = Chapter(
            id=ch['id'],
            title=ch['title'],
            content=ch.get('content'),  # Consider if content is needed for listings
            order=ch['order'],
            wordCount=ch['word_count'],
            readingTime=ch['reading_time'],
            createdAt=ch.get('created_at'),
            updatedAt=ch.get('updated_at')
        )
        chapters.append(chapter)

    return ChapterListResponse(
        chapters=chapters,
        total=chapters_data['total'],
        limit=limit,
        offset=offset
    )

@router.get("/chapters/{id}", response_model=Chapter)
@cached_endpoint(ttl=600)  # Cache for 10 minutes
async def get_chapter(id: str):
    """
    Retrieve a specific textbook chapter by ID.
    """
    chapter_data = content_service.get_chapter_by_id(id)
    if not chapter_data:
        raise HTTPException(status_code=404, detail=f"Chapter with id {id} not found")

    return Chapter(
        id=chapter_data['id'],
        title=chapter_data['title'],
        content=chapter_data.get('content'),
        order=chapter_data['order'],
        wordCount=chapter_data['word_count'],
        readingTime=chapter_data['reading_time'],
        createdAt=chapter_data.get('created_at'),
        updatedAt=chapter_data.get('updated_at')
    )

@router.get("/chapters/{id}/toc", response_model=TableOfContents)
@cached_endpoint(ttl=1800)  # Cache for 30 minutes (TOC changes less frequently)
async def get_chapter_toc(id: str):
    """
    Retrieve table of contents for a specific chapter.
    """
    toc_data = content_service.get_chapter_toc(id)
    if not toc_data:
        raise HTTPException(status_code=404, detail=f"Chapter with id {id} not found")

    return TableOfContents(
        chapterId=toc_data['chapterId'],
        title=toc_data['title'],
        sections=toc_data['sections']
    )


# New endpoints for optional features (translation and personalization)
@router.get("/chapters/translated", response_model=ChapterListResponse)
async def get_translated_chapters(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    language: str = Query("en", description="Target language code (e.g., 'ur' for Urdu)"),
    session_id: Optional[str] = Query(None, description="User session ID for personalization")
):
    """
    Retrieve all textbook chapters with optional translation and personalization.
    """
    # Determine if personalization should be applied
    personalization_enabled = session_id is not None

    chapters_data = content_service.get_all_chapters_with_options(
        limit=limit,
        offset=offset,
        language=language,
        personalization_enabled=personalization_enabled,
        session_id=session_id
    )

    # Convert to response format
    chapters = []
    for ch in chapters_data['chapters']:
        chapter = Chapter(
            id=ch['id'],
            title=ch['title'],
            content=ch.get('content'),
            order=ch['order'],
            wordCount=ch['word_count'],
            readingTime=ch['reading_time'],
            createdAt=ch.get('created_at'),
            updatedAt=ch.get('updated_at')
        )
        chapters.append(chapter)

    return ChapterListResponse(
        chapters=chapters,
        total=chapters_data['total'],
        limit=limit,
        offset=offset
    )


@router.get("/chapters/{id}/translated", response_model=Chapter)
async def get_translated_chapter(
    id: str,
    language: str = Query("en", description="Target language code (e.g., 'ur' for Urdu)"),
    session_id: Optional[str] = Query(None, description="User session ID for personalization")
):
    """
    Retrieve a specific textbook chapter by ID with optional translation and personalization.
    """
    # Determine if personalization should be applied
    personalization_enabled = session_id is not None

    chapter_data = content_service.get_chapter_by_id_with_options(
        id,
        language=language,
        personalization_enabled=personalization_enabled,
        session_id=session_id
    )

    if not chapter_data:
        raise HTTPException(status_code=404, detail=f"Chapter with id {id} not found")

    return Chapter(
        id=chapter_data['id'],
        title=chapter_data['title'],
        content=chapter_data.get('content'),
        order=chapter_data['order'],
        wordCount=chapter_data['word_count'],
        readingTime=chapter_data['reading_time'],
        createdAt=chapter_data.get('created_at'),
        updatedAt=chapter_data.get('updated_at')
    )