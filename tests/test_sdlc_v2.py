import pytest
from fastapi.testclient import TestClient
from api import app
from src.database.sdlc_db import SDLCDatabase

client = TestClient(app)

def test_create_project():
    response = client.post("/sdlc/v2/projects", json={
        "name": "Test Project",
        "repo_url": "https://github.com/mock/repo"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data

def test_generate_plan():
    # Create project first
    res = client.post("/sdlc/v2/projects", json={"name": "P1", "repo_url": "url"})
    pid = res.json()["id"]

    response = client.post(f"/sdlc/v2/projects/{pid}/plan")
    assert response.status_code == 200
    assert "plan_id" in response.json()

def test_get_status_empty():
    response = client.get("/sdlc/v2/projects/nonexistent/status")
    assert response.status_code == 200
    assert response.json()["tasks"] == []
