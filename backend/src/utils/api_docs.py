from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def customize_openapi(app: FastAPI):
    """Customize the OpenAPI documentation for the API"""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="AI-Native Textbook API",
            version="1.0.0",
            summary="API for textbook content and AI chatbot functionality",
            description="""
            This API provides access to textbook content and AI-powered Q&A functionality.

            ## Features
            * Access to textbook chapters and content
            * AI-powered question answering based on textbook content
            * Session management for user interactions
            * Health check endpoints for monitoring

            ## Authentication
            Most endpoints are public, but session-based authentication is available for personalized experiences.
            """,
            routes=app.routes,
        )

        # Add custom tags with descriptions
        openapi_schema["tags"] = [
            {
                "name": "textbook",
                "description": "Operations related to textbook content and chapters"
            },
            {
                "name": "ai",
                "description": "AI-powered question answering and chat functionality"
            },
            {
                "name": "health",
                "description": "Health check and system status endpoints"
            }
        ]

        # Add custom server information
        openapi_schema["servers"] = [
            {
                "url": "https://api.textbook.example.com",
                "description": "Production server"
            },
            {
                "url": "https://staging.api.textbook.example.com",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ]

        # Add security schemes if needed
        openapi_schema["components"] = openapi_schema.get("components", {})
        openapi_schema["components"]["securitySchemes"] = {
            "SessionToken": {
                "type": "apiKey",
                "in": "header",
                "name": "X-Session-Token",
                "description": "Session token for authenticated requests"
            }
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi


# Example usage in main app
def setup_api_documentation(app: FastAPI):
    """Set up API documentation for the application"""
    customize_openapi(app)