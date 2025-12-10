"""
Security Configuration
This module provides security-related utilities and configurations.
"""
from fastapi import FastAPI
from starlette.middleware.security import SecurityMiddleware
from starlette.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import List, Optional
from src.utils.logging import get_logger


logger = get_logger(__name__)


class SecurityConfig:
    """
    Security configuration class to manage security headers and settings
    """
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        logger.info("Security configuration initialized")

    def add_security_headers(self, response):
        """
        Add security headers to response
        """
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response

    def setup_security_middleware(self, app: FastAPI):
        """
        Setup security middleware for the FastAPI application
        """
        # Add security middleware
        app.add_middleware(
            SecurityMiddleware,
            hsts_max_age=31536000,
            hsts_include_subdomains=True,
            hsts_preload=True,
            permitted_cross_origin_policies="none",
        )

        # Add trusted host middleware - specify allowed hosts based on environment
        from src.utils.config import settings
        allowed_hosts = settings.allow_origins if settings.allow_origins != ["*"] else ["*"]
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )

        # Add GZip middleware for compression (also provides some security benefits)
        app.add_middleware(GZipMiddleware, minimum_size=1000)

        logger.info("Security middleware configured")


# Global instance
security_config = SecurityConfig()


def setup_security(app: FastAPI):
    """
    Apply security configurations to the FastAPI application
    """
    # Apply security middleware
    security_config.setup_security_middleware(app)

    # Add a middleware to add security headers to all responses
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response = security_config.add_security_headers(response)
        return response

    return app