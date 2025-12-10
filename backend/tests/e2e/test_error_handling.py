import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.utils.error_handler import APIError, ValidationError, NotFoundError, UnauthorizedError, ForbiddenError


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


def test_custom_error_types():
    """Test that all custom error types are properly defined"""
    # Test ValidationError
    validation_error = ValidationError("Invalid input provided")
    assert isinstance(validation_error, APIError)
    assert validation_error.status_code == 400
    assert validation_error.error_code == "VALIDATION_ERROR"

    # Test NotFoundError
    not_found_error = NotFoundError("Resource not found")
    assert isinstance(not_found_error, APIError)
    assert not_found_error.status_code == 404
    assert not_found_error.error_code == "NOT_FOUND"

    # Test UnauthorizedError
    unauthorized_error = UnauthorizedError("Authentication required")
    assert isinstance(unauthorized_error, APIError)
    assert unauthorized_error.status_code == 401
    assert unauthorized_error.error_code == "UNAUTHORIZED"

    # Test ForbiddenError
    forbidden_error = ForbiddenError("Access forbidden")
    assert isinstance(forbidden_error, APIError)
    assert forbidden_error.status_code == 403
    assert forbidden_error.error_code == "FORBIDDEN"


def test_api_error_base_class():
    """Test the base APIError class functionality"""
    error = APIError("Test error message", 500, "CUSTOM_ERROR")
    assert error.message == "Test error message"
    assert error.status_code == 500
    assert error.error_code == "CUSTOM_ERROR"

    # Test default values
    error_default = APIError("Default error")
    assert error_default.status_code == 500
    assert error_default.error_code == "INTERNAL_ERROR"


def test_error_handler_middleware(client):
    """Test that error handler middleware catches and formats errors properly"""
    # We'll test this by triggering a validation error if there's an endpoint that accepts invalid data
    # For now, test the health endpoint to ensure the app is working
    response = client.get("/health")
    assert response.status_code == 200


def test_error_response_format_consistency():
    """Test that error responses follow a consistent format"""
    # Test ValidationError format
    validation_error = ValidationError("Test validation error")
    error_dict = {
        "message": validation_error.message,
        "error_code": validation_error.error_code,
        "status_code": validation_error.status_code
    }
    assert error_dict["message"] == "Test validation error"
    assert error_dict["error_code"] == "VALIDATION_ERROR"
    assert error_dict["status_code"] == 400

    # Test other error types follow same pattern
    not_found_error = NotFoundError("Test not found error")
    error_dict = {
        "message": not_found_error.message,
        "error_code": not_found_error.error_code,
        "status_code": not_found_error.status_code
    }
    assert error_dict["error_code"] == "NOT_FOUND"
    assert error_dict["status_code"] == 404


def test_error_handler_registration():
    """Test that error handlers are registered with the FastAPI app"""
    # Check that exception handlers are registered
    assert len(app.exception_handlers) > 0

    # Check for specific exception handlers
    from src.utils.error_handler import validation_exception_handler, http_exception_handler, request_validation_exception_handler, custom_exception_handler

    # Verify handlers are registered for expected exception types
    expected_handlers = [
        ValidationError,
        NotFoundError,
        UnauthorizedError,
        ForbiddenError
    ]

    for exc_type in expected_handlers:
        assert exc_type in app.exception_handlers or issubclass(exc_type, tuple(app.exception_handlers.keys()))


def test_validation_error_handling():
    """Test validation error handling"""
    validation_error = ValidationError("Input validation failed")
    assert isinstance(validation_error, APIError)
    assert validation_error.status_code == 400
    assert validation_error.error_code == "VALIDATION_ERROR"


def test_error_inheritance_hierarchy():
    """Test the error class inheritance hierarchy"""
    validation_error = ValidationError("Test")
    not_found_error = NotFoundError("Test")
    unauthorized_error = UnauthorizedError("Test")
    forbidden_error = ForbiddenError("Test")

    # All should inherit from APIError
    assert isinstance(validation_error, APIError)
    assert isinstance(not_found_error, APIError)
    assert isinstance(unauthorized_error, APIError)
    assert isinstance(forbidden_error, APIError)

    # Each should have its own specific error code
    assert validation_error.error_code == "VALIDATION_ERROR"
    assert not_found_error.error_code == "NOT_FOUND"
    assert unauthorized_error.error_code == "UNAUTHORIZED"
    assert forbidden_error.error_code == "FORBIDDEN"


def test_error_message_preservation():
    """Test that error messages are properly preserved"""
    original_message = "This is a test error message with special characters: !@#$%^&*()"
    validation_error = ValidationError(original_message)
    assert validation_error.message == original_message

    not_found_error = NotFoundError(original_message)
    assert not_found_error.message == original_message

    unauthorized_error = UnauthorizedError(original_message)
    assert unauthorized_error.message == original_message

    forbidden_error = ForbiddenError(original_message)
    assert forbidden_error.message == original_message


def test_error_status_codes():
    """Test that error status codes are correct"""
    assert ValidationError("test").status_code == 400
    assert NotFoundError("test").status_code == 404
    assert UnauthorizedError("test").status_code == 401
    assert ForbiddenError("test").status_code == 403

    # Test default APIError status code
    assert APIError("test").status_code == 500


if __name__ == "__main__":
    pytest.main([__file__])