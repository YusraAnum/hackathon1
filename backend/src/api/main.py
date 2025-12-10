from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.utils.logging import log_api_call
from src.utils.api_docs import setup_api_documentation
from src.middleware.metrics_middleware import MetricsMiddleware, get_metrics_endpoint
from src.utils.error_handler import setup_error_handlers
from src.utils.security import setup_security

app = FastAPI(
    title="AI-Native Textbook API",
    description="""
    # AI-Native Textbook API

    This API provides access to textbook content and AI chatbot functionality for an AI-native textbook on Physical AI and Humanoid Robotics.

    ## Features
    - Access to textbook chapters and content
    - AI-powered Q&A system based on textbook content
    - Content translation and personalization
    - Performance monitoring and metrics

    ## Authentication
    Most endpoints are public. Some advanced features may require session tokens.

    ## Rate Limits
    API requests are subject to rate limiting to ensure fair usage.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "AI Textbook Support",
        "url": "https://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Set up API documentation
setup_api_documentation(app)

# Add metrics middleware first (so it captures all requests)
app.add_middleware(MetricsMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI-Native Textbook API is running!"}

from datetime import datetime

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    log_api_call("/health", "GET", status_code=200)
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "AI-Native Textbook API"
    }


@app.get("/metrics")
async def get_metrics():
    """Endpoint to retrieve performance metrics"""
    return await get_metrics_endpoint()

# Include API routes
from .textbook_routes import router as textbook_router
from .ai_routes import router as ai_router

app.include_router(textbook_router, prefix="/api/textbook", tags=["textbook"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])

# Initialize queue service workers
import asyncio
from src.services.queue_service import queue_service

# Setup security
app = setup_security(app)

# Setup error handlers
app = setup_error_handlers(app)

@app.on_event("startup")
async def startup_event():
    """Initialize queue service workers on startup"""
    await queue_service.start_workers()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up queue service workers on shutdown"""
    await queue_service.stop_workers()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)