import time
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, WebSocket
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import uuid
from datetime import datetime
import json
import asyncio
from src.services.queue_service import TaskStatus

router = APIRouter()

# Pydantic models for request/response
class AIQueryRequest(BaseModel):
    question: str
    context: Optional[str] = None
    sessionId: Optional[str] = None
    userId: Optional[str] = None

class Source(BaseModel):
    chapterId: str
    chapterTitle: str
    section: str
    confidence: float

class AIResponse(BaseModel):
    id: str
    queryId: str
    answer: str
    sources: List[Source]
    confidence: float
    timestamp: str

class AIQueryResponse(BaseModel):
    id: str
    queryId: str
    answer: str
    sources: List[Source]
    confidence: float
    timestamp: str

class SessionHistoryResponse(BaseModel):
    sessionId: str
    history: List[dict]
    createdAt: str
    lastActivity: str

class AIValidateRequest(BaseModel):
    question: str
    context: str

class AIValidateResponse(BaseModel):
    canAnswer: bool
    reason: str
    relevanceScore: float

@router.post("/query", response_model=AIResponse)
async def query_ai(request: AIQueryRequest):
    """
    Submit a question to the AI chatbot and receive a response based on textbook content.
    """
    # Generate IDs
    response_id = str(uuid.uuid4())
    query_id = str(uuid.uuid4())

    # Mock response - in real implementation, this would call the AI service
    answer = f"Based on the textbook content, I can provide information about: {request.question}"

    # Mock sources from textbook
    sources = [
        Source(
            chapterId="chapter-1",
            chapterTitle="Introduction to Physical AI",
            section="Core Principles",
            confidence=0.95
        )
    ]

    response = AIResponse(
        id=response_id,
        queryId=query_id,
        answer=answer,
        sources=sources,
        confidence=0.89,
        timestamp=datetime.now().isoformat()
    )

    return response

@router.post("/query/stream")
async def query_ai_stream(request: AIQueryRequest):
    """
    Submit a question to the AI chatbot and receive a streaming response.
    """
    # Generate IDs
    response_id = str(uuid.uuid4())
    query_id = str(uuid.uuid4())

    # Mock streaming response - in real implementation, this would stream from the AI service
    answer_parts = [
        "Based on the textbook content, ",
        "I can provide information about: ",
        request.question
    ]

    async def generate_stream():
        for i, part in enumerate(answer_parts):
            chunk = {
                "id": response_id,
                "queryId": query_id,
                "answer": part,
                "sources": [
                    {
                        "chapterId": "chapter-1",
                        "chapterTitle": "Introduction to Physical AI",
                        "section": "Core Principles",
                        "confidence": 0.95
                    }
                ],
                "confidence": 0.89,
                "timestamp": datetime.now().isoformat(),
                "done": i == len(answer_parts) - 1
            }
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@router.post("/validate", response_model=AIValidateResponse)
async def validate_question(request: AIValidateRequest):
    """
    Validate if a question can be answered based on textbook content.
    """
    # Simple mock validation - in real implementation, this would check against embeddings
    is_relevant = len(request.question.split()) > 2  # Basic check

    if is_relevant:
        return AIValidateResponse(
            canAnswer=True,
            reason="Question appears to be related to textbook content",
            relevanceScore=0.8
        )
    else:
        return AIValidateResponse(
            canAnswer=False,
            reason="Question is too vague or outside the scope of textbook content",
            relevanceScore=0.2
        )

from src.services.session_service import session_service
from src.services.queue_service import queue_service


@router.post("/query", response_model=AIResponse)
async def query_ai(request: AIQueryRequest):
    """
    Submit a question to the AI chatbot and receive a response based on textbook content.
    This endpoint now uses request queuing to manage load.
    """
    # Submit the task to the queue
    task_id = await queue_service.submit_task(
        task_type="ai_query",
        payload={
            "query": request.question,
            "context": request.context,
            "user_id": request.userId,
            "question": request.question  # For RAG context retrieval
        }
    )

    # Wait for the task to complete (with timeout)
    max_wait_time = 30  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        task_status = queue_service.get_task_status(task_id)
        if task_status and task_status.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            if task_status.status == TaskStatus.COMPLETED:
                # Generate IDs for response
                response_id = str(uuid.uuid4())

                # Mock sources from textbook (in real implementation, these would come from the RAG system)
                sources = [
                    Source(
                        chapterId="chapter-1",
                        chapterTitle="Introduction to Physical AI",
                        section="Core Principles",
                        confidence=0.95
                    )
                ]

                response = AIResponse(
                    id=response_id,
                    queryId=task_id,
                    answer=task_status.result,
                    sources=sources,
                    confidence=0.89,
                    timestamp=datetime.now().isoformat()
                )

                return response
            else:
                raise HTTPException(status_code=500, detail=f"AI query failed: {task_status.error}")

        await asyncio.sleep(0.5)  # Wait 0.5 seconds before checking again

    # If we've waited too long, return a queued response
    raise HTTPException(status_code=202, detail="Request is being processed, please check status later")


@router.get("/query/{task_id}", response_model=AIResponse)
async def get_query_result(task_id: str):
    """
    Get the result of a queued AI query.
    """
    task_status = queue_service.get_task_status(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_status.status == TaskStatus.PENDING or task_status.status == TaskStatus.PROCESSING:
        raise HTTPException(status_code=202, detail="Task is still processing")
    elif task_status.status == TaskStatus.FAILED:
        raise HTTPException(status_code=500, detail=f"Task failed: {task_status.error}")
    elif task_status.status == TaskStatus.COMPLETED:
        # Generate response with the completed result
        response_id = str(uuid.uuid4())

        # Mock sources from textbook (in real implementation, these would come from the RAG system)
        sources = [
            Source(
                chapterId="chapter-1",
                chapterTitle="Introduction to Physical AI",
                section="Core Principles",
                confidence=0.95
            )
        ]

        response = AIResponse(
            id=response_id,
            queryId=task_id,
            answer=task_status.result,
            sources=sources,
            confidence=0.89,
            timestamp=datetime.now().isoformat()
        )

        return response


@router.get("/queue/status")
async def get_queue_status():
    """
    Get the current status of the AI query queue.
    """
    return {
        "queue_size": queue_service.get_queue_size(),
        "active_tasks": len(queue_service.active_tasks),
        "max_concurrent": queue_service.max_concurrent
    }


@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """
    Retrieve conversation history for a specific session.
    """
    # Get session from session service
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get session history from session service
    history = session_service.get_session_history(session_id)

    # Get the session creation time and last activity
    created_at = session.start_time.isoformat() if session.start_time else datetime.now().isoformat()
    last_activity = session.last_activity.isoformat() if session.last_activity else datetime.now().isoformat()

    return SessionHistoryResponse(
        sessionId=session_id,
        history=history,
        createdAt=created_at,
        lastActivity=last_activity
    )