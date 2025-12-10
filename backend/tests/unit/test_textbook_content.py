import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.services.content_service import content_service


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


def test_get_chapters(client):
    """Test the GET /api/textbook/chapters endpoint"""
    response = client.get("/api/textbook/chapters")
    assert response.status_code == 200

    data = response.json()
    assert "chapters" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 10  # Default limit


def test_get_chapters_with_params(client):
    """Test the GET /api/textbook/chapters endpoint with query parameters"""
    response = client.get("/api/textbook/chapters?limit=5&offset=0")
    assert response.status_code == 200

    data = response.json()
    assert "chapters" in data
    assert len(data["chapters"]) <= 5
    assert data["limit"] == 5


def test_get_chapter_by_id(client):
    """Test the GET /api/textbook/chapters/{id} endpoint"""
    # First get a list of chapters to find a valid ID
    chapters_response = client.get("/api/textbook/chapters")
    chapters_data = chapters_response.json()

    if chapters_data["chapters"]:
        chapter_id = chapters_data["chapters"][0]["id"]
        response = client.get(f"/api/textbook/chapters/{chapter_id}")
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "title" in data
        assert data["id"] == chapter_id


def test_get_chapter_toc(client):
    """Test the GET /api/textbook/chapters/{id}/toc endpoint"""
    # First get a list of chapters to find a valid ID
    chapters_response = client.get("/api/textbook/chapters")
    chapters_data = chapters_response.json()

    if chapters_data["chapters"]:
        chapter_id = chapters_data["chapters"][0]["id"]
        response = client.get(f"/api/textbook/chapters/{chapter_id}/toc")
        assert response.status_code == 200

        data = response.json()
        assert "chapterId" in data
        assert "title" in data
        assert "sections" in data
        assert data["chapterId"] == chapter_id


def test_get_nonexistent_chapter(client):
    """Test getting a non-existent chapter"""
    response = client.get("/api/textbook/chapters/nonexistent-chapter")
    assert response.status_code == 404


def test_get_nonexistent_chapter_toc(client):
    """Test getting TOC for a non-existent chapter"""
    response = client.get("/api/textbook/chapters/nonexistent-chapter/toc")
    assert response.status_code == 404


def test_content_service_loads_chapters():
    """Test that the content service can load chapters from files"""
    chapters_data = content_service.get_all_chapters(limit=100, offset=0)

    assert "chapters" in chapters_data
    assert "total" in chapters_data
    assert chapters_data["total"] >= 0  # May be 0 if no content files exist yet

    # If there are chapters, verify they have required fields
    if chapters_data["chapters"]:
        chapter = chapters_data["chapters"][0]
        assert "id" in chapter
        assert "title" in chapter
        assert "order" in chapter


def test_content_service_get_chapter_by_id():
    """Test getting a specific chapter by ID using content service"""
    chapters_data = content_service.get_all_chapters(limit=1, offset=0)

    if chapters_data["chapters"]:
        chapter_id = chapters_data["chapters"][0]["id"]
        chapter_data = content_service.get_chapter_by_id(chapter_id)

        assert chapter_data is not None
        assert chapter_data["id"] == chapter_id
        assert "title" in chapter_data


def test_content_service_get_chapter_toc():
    """Test getting chapter TOC using content service"""
    chapters_data = content_service.get_all_chapters(limit=1, offset=0)

    if chapters_data["chapters"]:
        chapter_id = chapters_data["chapters"][0]["id"]
        toc_data = content_service.get_chapter_toc(chapter_id)

        assert toc_data is not None
        assert toc_data["chapterId"] == chapter_id
        assert "sections" in toc_data