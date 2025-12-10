import logging
import sys
from datetime import datetime
from typing import Any, Dict
from fastapi import HTTPException
from src.utils.config import settings
from .comprehensive_logging import get_logger as get_comprehensive_logger, LogMetadata


def setup_logging():
    """Set up basic logging configuration"""
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Set specific loggers to WARNING level to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str):
    """Get a comprehensive logger with structured logging capabilities"""
    return get_comprehensive_logger(name)


class CustomException(HTTPException):
    """Custom exception class with logging"""
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        logger = get_logger(__name__)
        logger.error(
            f"CustomException: status_code={status_code}, detail={detail}, error_code={error_code}",
            extra_data={"status_code": status_code, "error_code": error_code}
        )


def log_exception(exc: Exception, context: str = ""):
    """Log exception with context"""
    logger = get_logger(__name__)
    logger.error(
        f"Exception in {context}: {type(exc).__name__} - {str(exc)}",
        extra_data={"context": context, "exception_type": type(exc).__name__},
        metadata=LogMetadata()
    )


def log_api_call(endpoint: str, method: str, user_id: str = None, status_code: int = 200,
                 response_time: float = None, ip_address: str = None):
    """Log API call information"""
    logger = get_logger("api")
    logger.log_api_call(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time=response_time,
        user_id=user_id,
        ip_address=ip_address
    )


# Initialize logging
setup_logging()