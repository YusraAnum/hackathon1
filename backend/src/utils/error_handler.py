"""
Comprehensive Error Handler
This module provides centralized error handling for the backend API.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from src.utils.logging import get_logger
import traceback
import sys


logger = get_logger(__name__)


class APIError(Exception):
    """Base API Exception class"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation Error"""
    def __init__(self, message: str):
        super().__init__(message, 400, "VALIDATION_ERROR")


class NotFoundError(APIError):
    """Not Found Error"""
    def __init__(self, message: str):
        super().__init__(message, 404, "NOT_FOUND_ERROR")


class UnauthorizedError(APIError):
    """Unauthorized Error"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, 401, "UNAUTHORIZED_ERROR")


class ForbiddenError(APIError):
    """Forbidden Error"""
    def __init__(self, message: str = "Forbidden access"):
        super().__init__(message, 403, "FORBIDDEN_ERROR")


def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for FastAPI
    """
    # Log the error with full traceback
    error_id = f"error_{hash(str(exc)) % 1000000}"
    logger.error(f"Error ID: {error_id} - {str(exc)}", exc_info=True)

    # Determine error type and response
    if isinstance(exc, APIError):
        status_code = exc.status_code
        error_code = exc.error_code
        message = exc.message
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_code = f"HTTP_{exc.status_code}"
        message = exc.detail
    else:
        # Internal server error for unhandled exceptions
        status_code = 500
        error_code = "INTERNAL_ERROR"
        message = "An internal server error occurred"

    # Don't expose internal error details in production
    if status_code == 500:
        message = "An internal server error occurred"
        logger.error(f"Internal server error ID: {error_id}")

    from datetime import datetime
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


def setup_error_handlers(app):
    """
    Setup error handlers for the FastAPI application
    """
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return exception_handler(request, exc)

    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError):
        return exception_handler(request, exc)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        return exception_handler(request, exc)

    return app


def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Handle an error and return a structured error response

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred

    Returns:
        Dictionary with error information
    """
    error_id = f"error_{hash(str(error)) % 1000000}"
    error_msg = str(error)

    # Log the error
    logger.error(f"Error ID: {error_id} - Context: {context} - Error: {error_msg}", exc_info=True)

    # Determine error type
    if isinstance(error, APIError):
        status_code = error.status_code
        error_code = error.error_code
    elif isinstance(error, HTTPException):
        status_code = error.status_code
        error_code = f"HTTP_{error.status_code}"
        error_msg = error.detail
    else:
        status_code = 500
        error_code = "INTERNAL_ERROR"

    return {
        "error": {
            "code": error_code,
            "message": error_msg,
            "error_id": error_id,
            "context": context
        },
        "status_code": status_code
    }