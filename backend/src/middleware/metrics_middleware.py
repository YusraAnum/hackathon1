import time
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from src.services.metrics_service import metrics_service
from src.utils.logging import get_logger


logger = get_logger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track performance metrics for all requests
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Get endpoint path
        endpoint = request.url.path

        # Determine if it was an error based on status code
        is_error = response.status_code >= 400

        # Record metrics
        metrics_service.record_request(
            endpoint=endpoint,
            response_time=response_time,
            is_error=is_error
        )

        # Add response time header for debugging (optional)
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"

        return response


async def get_metrics_endpoint():
    """
    API endpoint to retrieve collected metrics
    """
    return metrics_service.get_all_metrics()