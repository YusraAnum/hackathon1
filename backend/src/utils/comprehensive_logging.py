"""
Comprehensive Logging System
This module provides enhanced logging capabilities for the application.
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json
import traceback
from enum import Enum


class LogLevel(Enum):
    """Log level enum"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogMetadata:
    """Log metadata for structured logging"""
    def __init__(self,
                 user_id: Optional[str] = None,
                 session_id: Optional[str] = None,
                 request_id: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 method: Optional[str] = None,
                 ip_address: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id
        self.endpoint = endpoint
        self.method = method
        self.ip_address = ip_address


class StructuredLogger:
    """Structured logger that outputs JSON format logs"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            # Create console handler with a higher log level
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)

            # Create formatter that outputs JSON
            formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            self.logger.addHandler(console_handler)
            self.logger.propagate = False

    def _format_log(self, level: LogLevel, message: str, metadata: Optional[LogMetadata] = None,
                   extra_data: Optional[Dict[str, Any]] = None) -> str:
        """Format log message as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "message": message,
            "logger": self.logger.name
        }

        if metadata:
            if metadata.user_id:
                log_entry["user_id"] = metadata.user_id
            if metadata.session_id:
                log_entry["session_id"] = metadata.session_id
            if metadata.request_id:
                log_entry["request_id"] = metadata.request_id
            if metadata.endpoint:
                log_entry["endpoint"] = metadata.endpoint
            if metadata.method:
                log_entry["method"] = metadata.method
            if metadata.ip_address:
                log_entry["ip_address"] = metadata.ip_address

        if extra_data:
            log_entry["extra"] = extra_data

        # Add stack trace for error and critical logs
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            log_entry["stack_trace"] = traceback.format_stack()

        return json.dumps(log_entry)

    def debug(self, message: str, metadata: Optional[LogMetadata] = None,
              extra_data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        formatted_log = self._format_log(LogLevel.DEBUG, message, metadata, extra_data)
        self.logger.debug(formatted_log)

    def info(self, message: str, metadata: Optional[LogMetadata] = None,
             extra_data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        formatted_log = self._format_log(LogLevel.INFO, message, metadata, extra_data)
        self.logger.info(formatted_log)

    def warning(self, message: str, metadata: Optional[LogMetadata] = None,
                extra_data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        formatted_log = self._format_log(LogLevel.WARNING, message, metadata, extra_data)
        self.logger.warning(formatted_log)

    def error(self, message: str, metadata: Optional[LogMetadata] = None,
              extra_data: Optional[Dict[str, Any]] = None):
        """Log error message"""
        formatted_log = self._format_log(LogLevel.ERROR, message, metadata, extra_data)
        self.logger.error(formatted_log)

    def critical(self, message: str, metadata: Optional[LogMetadata] = None,
                 extra_data: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        formatted_log = self._format_log(LogLevel.CRITICAL, message, metadata, extra_data)
        self.logger.critical(formatted_log)

    def log_api_call(self, endpoint: str, method: str, status_code: int,
                     response_time: Optional[float] = None,
                     user_id: Optional[str] = None,
                     ip_address: Optional[str] = None):
        """Log API call with structured data"""
        extra_data = {
            "status_code": status_code
        }
        if response_time:
            extra_data["response_time_ms"] = round(response_time * 1000, 2)

        metadata = LogMetadata(
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            ip_address=ip_address
        )

        self.info(f"API call completed: {method} {endpoint}", metadata=metadata, extra_data=extra_data)

    def log_database_operation(self, operation: str, table: str,
                              success: bool, execution_time: Optional[float] = None,
                              records_affected: Optional[int] = None):
        """Log database operation"""
        extra_data = {
            "operation": operation,
            "table": table,
            "success": success
        }
        if execution_time:
            extra_data["execution_time_ms"] = round(execution_time * 1000, 2)
        if records_affected is not None:
            extra_data["records_affected"] = records_affected

        status = "successful" if success else "failed"
        self.info(f"Database operation {status}: {operation} on {table}",
                  extra_data=extra_data)

    def log_security_event(self, event_type: str, user_id: Optional[str] = None,
                          ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log security-related events"""
        extra_data = {
            "event_type": event_type
        }
        if details:
            extra_data.update(details)

        metadata = LogMetadata(user_id=user_id, ip_address=ip_address)

        self.warning(f"Security event: {event_type}", metadata=metadata, extra_data=extra_data)


# Global logger instance
comprehensive_logger = StructuredLogger(__name__)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)