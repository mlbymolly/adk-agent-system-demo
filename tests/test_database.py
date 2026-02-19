"""Tests for database modules — DB_PATH configurability and CRUD operations."""

import os
import tempfile
import sqlite3

import pytest

from src.database.session_db import Database, DEFAULT_DB_PATH
from src.database.task_db import TaskDatabase, DEFAULT_DB_PATH as TASK_DEFAULT_DB_PATH


# ==================== DB_PATH Configurability ====================


class TestDBPathConfig:
    """Verify the DB_PATH environment variable is respected."""

    def test_default_db_path_without_env(self, monkeypatch):
        """When DB_PATH is unset, default should be 'assistant.db'."""
        monkeypatch.delenv("DB_PATH", raising=False)
        # Re-import to pick up the env change
        import importlib
        import src.database.session_db as sdb
        import src.database.task_db as tdb
        importlib.reload(sdb)
        importlib.reload(tdb)
        assert sdb.DEFAULT_DB_PATH == "assistant.db"
        assert tdb.DEFAULT_DB_PATH == "assistant.db"

    def test_db_path_from_env(self, monkeypatch):
        """When DB_PATH is set, modules should use it as default."""
        monkeypatch.setenv("DB_PATH", "/app/data/custom.db")
        import importlib
        import src.database.session_db as sdb
        import src.database.task_db as tdb
        importlib.reload(sdb)
        importlib.reload(tdb)
        assert sdb.DEFAULT_DB_PATH == "/app/data/custom.db"
        assert tdb.DEFAULT_DB_PATH == "/app/data/custom.db"

    def test_explicit_path_overrides_env(self, monkeypatch, tmp_path):
        """Passing db_path explicitly should override the env var."""
        monkeypatch.setenv("DB_PATH", "/should/not/be/used.db")
        explicit = str(tmp_path / "explicit.db")
        db = Database(db_path=explicit)
        assert db.db_path == explicit

    def test_session_and_task_db_share_same_file(self, tmp_db_path):
        """Both Database and TaskDatabase should use the same file."""
        sdb = Database(db_path=tmp_db_path)
        tdb = TaskDatabase(db_path=tmp_db_path)
        assert sdb.db_path == tdb.db_path

    def test_database_creates_file(self, tmp_path):
        """Initialising a Database should create the .db file."""
        path = str(tmp_path / "new.db")
        assert not os.path.exists(path)
        Database(db_path=path)
        assert os.path.exists(path)

    def test_task_database_creates_file(self, tmp_path):
        """Initialising a TaskDatabase should create the .db file."""
        path = str(tmp_path / "new_task.db")
        assert not os.path.exists(path)
        TaskDatabase(db_path=path)
        assert os.path.exists(path)


# ==================== Session Database CRUD ====================


class TestSessionDatabase:
    """Unit tests for session_db.Database."""

    def test_create_session(self, session_db):
        result = session_db.create_session("s1", "alice", "app")
        assert result["session_id"] == "s1"
        assert result["user_id"] == "alice"
        assert result["app_name"] == "app"
        assert "created_at" in result

    def test_get_session(self, session_db):
        session_db.create_session("s1", "alice", "app")
        result = session_db.get_session("s1")
        assert result is not None
        assert result["session_id"] == "s1"

    def test_get_session_not_found(self, session_db):
        result = session_db.get_session("nonexistent")
        assert result is None

    def test_get_all_sessions(self, session_db):
        session_db.create_session("s1", "alice", "app")
        session_db.create_session("s2", "bob", "app")
        all_sessions = session_db.get_all_sessions()
        assert len(all_sessions) == 2

    def test_get_all_sessions_filtered(self, session_db):
        session_db.create_session("s1", "alice", "app")
        session_db.create_session("s2", "bob", "app")
        alice_sessions = session_db.get_all_sessions(user_id="alice")
        assert len(alice_sessions) == 1
        assert alice_sessions[0]["user_id"] == "alice"

    def test_add_and_get_messages(self, session_db):
        session_db.create_session("s1", "alice", "app")
        session_db.add_message("s1", "user", "hello")
        session_db.add_message("s1", "assistant", "hi there")
        messages = session_db.get_messages("s1")
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_get_messages_with_limit(self, session_db):
        session_db.create_session("s1", "alice", "app")
        for i in range(5):
            session_db.add_message("s1", "user", f"msg {i}")
        messages = session_db.get_messages("s1", limit=3)
        assert len(messages) == 3

    def test_delete_session(self, session_db):
        session_db.create_session("s1", "alice", "app")
        session_db.add_message("s1", "user", "hello")
        assert session_db.delete_session("s1") is True
        assert session_db.get_session("s1") is None
        assert session_db.get_messages("s1") == []

    def test_delete_session_not_found(self, session_db):
        assert session_db.delete_session("nonexistent") is False

    def test_clear_all_sessions(self, session_db):
        session_db.create_session("s1", "alice", "app")
        session_db.create_session("s2", "bob", "app")
        session_db.clear_all_sessions()
        assert session_db.get_all_sessions() == []


# ==================== Task Database CRUD ====================


class TestTaskDatabase:
    """Unit tests for task_db.TaskDatabase."""

    def test_create_task(self, task_db):
        task = task_db.create_task(title="Buy milk", priority="high", user_id="alice")
        assert task["title"] == "Buy milk"
        assert task["priority"] == "high"
        assert task["status"] == "pending"
        assert task["id"] is not None

    def test_get_task(self, task_db):
        created = task_db.create_task(title="Test")
        fetched = task_db.get_task(created["id"])
        assert fetched is not None
        assert fetched["title"] == "Test"

    def test_get_task_not_found(self, task_db):
        assert task_db.get_task(9999) is None

    def test_get_all_tasks(self, task_db):
        task_db.create_task(title="A")
        task_db.create_task(title="B")
        tasks = task_db.get_all_tasks()
        assert len(tasks) == 2

    def test_get_all_tasks_filter_status(self, task_db):
        task_db.create_task(title="A", status="pending")
        task_db.create_task(title="B", status="completed")
        pending = task_db.get_all_tasks(status="pending")
        assert len(pending) == 1
        assert pending[0]["title"] == "A"

    def test_get_all_tasks_filter_priority(self, task_db):
        task_db.create_task(title="A", priority="high")
        task_db.create_task(title="B", priority="low")
        high = task_db.get_all_tasks(priority="high")
        assert len(high) == 1

    def test_update_task(self, task_db):
        task = task_db.create_task(title="Old")
        updated = task_db.update_task(task["id"], title="New")
        assert updated["title"] == "New"

    def test_update_task_status_completed_sets_completed_at(self, task_db):
        task = task_db.create_task(title="Do it")
        updated = task_db.update_task(task["id"], status="completed")
        assert updated["status"] == "completed"
        assert updated["completed_at"] is not None

    def test_update_task_not_found(self, task_db):
        result = task_db.update_task(9999, title="Nope")
        assert result is None

    def test_delete_task(self, task_db):
        task = task_db.create_task(title="Delete me")
        assert task_db.delete_task(task["id"]) is True
        assert task_db.get_task(task["id"]) is None

    def test_delete_task_not_found(self, task_db):
        assert task_db.delete_task(9999) is False

    def test_search_tasks(self, task_db):
        task_db.create_task(title="Buy groceries", description="milk and eggs")
        task_db.create_task(title="Write report")
        results = task_db.search_tasks("groceries")
        assert len(results) == 1
        assert results[0]["title"] == "Buy groceries"

    def test_search_tasks_by_description(self, task_db):
        task_db.create_task(title="Shopping", description="buy milk and eggs")
        results = task_db.search_tasks("milk")
        assert len(results) == 1

    def test_get_tasks_by_location(self, task_db):
        task_db.create_task(title="A", location="New York")
        task_db.create_task(title="B", location="London")
        results = task_db.get_tasks_by_location("New York")
        assert len(results) == 1
        assert results[0]["location"] == "New York"

    def test_get_task_statistics(self, task_db):
        task_db.create_task(title="A", status="pending", priority="high")
        task_db.create_task(title="B", status="completed", priority="low")
        stats = task_db.get_task_statistics()
        assert stats["total_tasks"] == 2
        assert stats["by_status"]["pending"] == 1
        assert stats["by_status"]["completed"] == 1
        assert stats["by_priority"]["high"] == 1
        assert stats["by_priority"]["low"] == 1

    def test_get_tasks_by_date_range(self, task_db):
        task_db.create_task(title="A", due_date="2025-01-01")
        task_db.create_task(title="B", due_date="2025-06-15")
        task_db.create_task(title="C", due_date="2025-12-31")
        results = task_db.get_tasks_by_date_range("2025-01-01", "2025-06-30")
        assert len(results) == 2
