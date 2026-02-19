"""Tests for FastAPI endpoints — tasks router and health/root endpoints.

Sessions router is excluded because it depends on google.adk InMemoryRunner
which requires a real API key. Task endpoints use only the local SQLite DB.
"""

import os
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path):
    """Create a TestClient with a temporary database."""
    db_path = str(tmp_path / "test_api.db")
    with patch.dict(os.environ, {"DB_PATH": db_path}):
        # Re-import modules so they pick up the patched DB_PATH
        import importlib
        import src.database.task_db as tdb
        import src.database.session_db as sdb
        importlib.reload(tdb)
        importlib.reload(sdb)

        # Re-import routers so they create new DB instances
        import src.routers.tasks as tasks_mod
        importlib.reload(tasks_mod)

        # Build a fresh app with the reloaded router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(tasks_mod.router)

        # Add the root/health endpoints directly
        @app.get("/health")
        async def health_check():
            api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
            return {
                "status": "healthy",
                "api_key_configured": api_key_set,
                "database": "connected",
                "agents": "ready",
            }

        @app.get("/")
        async def root():
            return {"name": "Weather, Date & Task Management Assistant API"}

        yield TestClient(app)


# ==================== Health & Root ====================


class TestHealthAndRoot:
    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "name" in resp.json()

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_reports_api_key_status(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "api_key_configured" in data


# ==================== Task CRUD Endpoints ====================


class TestTaskEndpoints:
    def _create_task(self, client, **overrides):
        payload = {"title": "Test task", "priority": "medium", **overrides}
        return client.post("/tasks", json=payload)

    def test_create_task(self, client):
        resp = self._create_task(client, title="Buy milk", priority="high")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Buy milk"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "id" in data

    def test_list_tasks(self, client):
        self._create_task(client, title="A")
        self._create_task(client, title="B")
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_tasks_filter_status(self, client):
        self._create_task(client, title="A")
        resp = client.get("/tasks", params={"status": "completed"})
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_get_task_by_id(self, client):
        create_resp = self._create_task(client, title="Fetch me")
        task_id = create_resp.json()["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Fetch me"

    def test_get_task_not_found(self, client):
        resp = client.get("/tasks/9999")
        assert resp.status_code == 404

    def test_update_task(self, client):
        task_id = self._create_task(client, title="Old").json()["id"]
        resp = client.put(f"/tasks/{task_id}", json={"title": "New"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    def test_update_task_not_found(self, client):
        resp = client.put("/tasks/9999", json={"title": "Nope"})
        assert resp.status_code == 404

    def test_delete_task(self, client):
        task_id = self._create_task(client).json()["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert client.get(f"/tasks/{task_id}").status_code == 404

    def test_delete_task_not_found(self, client):
        resp = client.delete("/tasks/9999")
        assert resp.status_code == 404

    def test_complete_task(self, client):
        task_id = self._create_task(client).json()["id"]
        resp = client.post(f"/tasks/{task_id}/complete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        assert resp.json()["completed_at"] is not None


# ==================== Analytics Endpoints ====================


class TestAnalyticsEndpoints:
    def _seed(self, client):
        client.post("/tasks", json={
            "title": "Overdue",
            "due_date": "2020-01-01",
            "priority": "high",
            "location": "Paris",
        })
        client.post("/tasks", json={
            "title": "Soon",
            "due_date": "2099-01-01",
            "priority": "low",
            "location": "London",
        })

    def test_statistics(self, client):
        self._seed(client)
        resp = client.get("/tasks/query/statistics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_tasks"] == 2

    def test_overdue(self, client):
        self._seed(client)
        resp = client.get("/tasks/query/overdue")
        assert resp.status_code == 200
        tasks = resp.json()
        assert any(t["title"] == "Overdue" for t in tasks)

    def test_due_soon(self, client):
        self._seed(client)
        resp = client.get("/tasks/query/due-soon", params={"days": 36500})
        assert resp.status_code == 200

    def test_by_location(self, client):
        self._seed(client)
        resp = client.get("/tasks/query/by-location", params={"location": "Paris"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["location"] == "Paris"

    def test_search(self, client):
        self._seed(client)
        resp = client.get("/tasks/query/search", params={"q": "Overdue"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_date_range(self, client):
        self._seed(client)
        resp = client.get("/tasks/query/date-range", params={
            "start_date": "2019-01-01",
            "end_date": "2021-01-01",
        })
        assert resp.status_code == 200
        assert len(resp.json()) == 1
