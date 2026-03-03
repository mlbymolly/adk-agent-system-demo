import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "api_key_configured" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Multi-Agent System API"
    assert "version" in data

def test_sdlc_endpoints_exist():
    # Test that the SDLC routes are registered
    response = client.get("/sdlc/issues")
    assert response.status_code == 200
    assert response.json()["message"] == "List of issues"

    response = client.get("/sdlc/pull-requests")
    assert response.status_code == 200
    assert response.json()["message"] == "List of pull requests"

@patch("src.routers.sdlc_router.InMemoryRunner")
def test_sdlc_chat_endpoint_mocked(mock_runner):
    # Mock the runner to avoid needing a real API key
    mock_instance = mock_runner.return_value
    mock_instance.session_service.create_session = AsyncMock()

    # Mock the async generator for run_async
    async def mock_run_async(*args, **kwargs):
        class MockEvent:
            def __init__(self, text):
                self.content = AsyncMock()
                self.content.parts = [AsyncMock(text=text)]
        yield MockEvent("Mocked agent response")

    mock_instance.run_async = mock_run_async

    response = client.post("/sdlc/chat", json={
        "session_id": "test_session",
        "message": "hello",
        "user_id": "test_user"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test_session"
    assert data["assistant_message"] == "Mocked agent response"
