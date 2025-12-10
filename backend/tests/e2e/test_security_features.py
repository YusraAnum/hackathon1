import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.utils.security import SecurityConfig, security_middleware
from src.utils.error_handler import APIError, ValidationError, NotFoundError, UnauthorizedError, ForbiddenError


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


def test_security_headers_present(client):
    """Test that all security headers are present in responses"""
    response = client.get("/")
    headers = response.headers

    # Check all security headers are present
    security_config = SecurityConfig()

    for header_name, expected_value in security_config.security_headers.items():
        # Convert to lowercase since HTTP headers are case-insensitive
        found = False
        for response_header in headers:
            if response_header.lower() == header_name.lower():
                found = True
                break
        assert found, f"Security header {header_name} not found in response"


def test_security_middleware_application(client):
    """Test that security middleware is properly applied"""
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200

    # Check security headers are applied
    headers = response.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") in ["DENY", "SAMEORIGIN"]
    assert headers.get("x-xss-protection") == "1; mode=block"


def test_cors_security(client):
    """Test CORS-related security headers"""
    response = client.get("/")
    headers = response.headers

    # Check for referrer policy
    assert headers.get("referrer-policy") is not None

    # Check for permissions policy
    assert headers.get("permissions-policy") is not None


def test_security_config_initialization():
    """Test that security configuration is properly initialized"""
    config = SecurityConfig()
    assert config.security_headers is not None
    assert isinstance(config.security_headers, dict)
    assert len(config.security_headers) > 0

    # Check that all expected security headers are present
    expected_headers = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Referrer-Policy",
        "Permissions-Policy"
    ]

    for header in expected_headers:
        assert header in config.security_headers


def test_security_middleware_functionality():
    """Test security middleware functionality"""
    # This tests that the middleware function is properly defined
    assert callable(security_middleware)


def test_https_redirect_simulation():
    """Test HTTPS redirect behavior (simulated)"""
    # In production, this would redirect HTTP to HTTPS
    # For testing, we verify the configuration is correct
    config = SecurityConfig()
    hsts_header = config.security_headers.get("Strict-Transport-Security")
    assert hsts_header is not None
    assert "max-age" in hsts_header


def test_content_security_simulation():
    """Test content security measures (simulated)"""
    # Test that frame options are properly set to prevent clickjacking
    config = SecurityConfig()
    x_frame_options = config.security_headers.get("X-Frame-Options")
    assert x_frame_options in ["DENY", "SAMEORIGIN"]


def test_xss_protection_enabled(client):
    """Test that XSS protection is enabled"""
    response = client.get("/")
    headers = response.headers
    xss_protection = headers.get("x-xss-protection")
    assert xss_protection in ["1", "1; mode=block"]


def test_content_type_options(client):
    """Test that content type options are set to prevent MIME type sniffing"""
    response = client.get("/")
    headers = response.headers
    content_type_options = headers.get("x-content-type-options")
    assert content_type_options == "nosniff"


def test_security_headers_on_error_responses(client):
    """Test that security headers are present even on error responses"""
    # Test with a non-existent endpoint to trigger an error
    response = client.get("/nonexistent-endpoint")

    # Even on error, security headers should be present
    headers = response.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-xss-protection") is not None


if __name__ == "__main__":
    pytest.main([__file__])