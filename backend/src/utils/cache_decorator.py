import functools
import hashlib
from typing import Callable, Any
from fastapi import Request, Response
from src.services.cache_service import cache_service
from src.utils.logging import get_logger


logger = get_logger(__name__)


def cached_endpoint(ttl: int = 300, include_query_params: bool = True, include_body: bool = False):
    """
    Decorator to cache API endpoint responses
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from kwargs or args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break

            if request:
                # Generate cache key based on endpoint path and parameters
                path = request.url.path
                query_params = ""
                if include_query_params:
                    query_params = str(sorted(request.query_params.items()))

                body_content = ""
                if include_body:
                    # This is a simplified approach - in practice you'd need to handle request body differently
                    # as it's an async stream
                    body_content = str(kwargs.get('body', ''))

                cache_key = f"endpoint:{path}:{query_params}:{body_content}"
                cache_key = hashlib.md5(cache_key.encode()).hexdigest()

                # Try to get from cache first
                cached_result = cache_service.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"API cache hit for endpoint: {path}")
                    return cached_result

                # Execute the original function
                result = await func(*args, **kwargs)

                # Cache the result
                cache_service.set(cache_key, result, ttl=ttl)
                logger.debug(f"API cache set for endpoint: {path} with TTL: {ttl}s")

                return result
            else:
                # If no request object, just execute the function
                return await func(*args, **kwargs)

        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Helper function to invalidate cache entries matching a pattern
    """
    count = cache_service.invalidate_pattern(pattern)
    logger.info(f"Invalidated {count} cache entries matching pattern: {pattern}")
    return count