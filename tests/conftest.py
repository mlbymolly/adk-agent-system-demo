"""Shared test fixtures."""

import os
import tempfile
import pytest

from src.database.session_db import Database
from src.database.task_db import TaskDatabase


@pytest.fixture()
def tmp_db_path(tmp_path):
    """Return a temporary database file path."""
    return str(tmp_path / "test.db")


@pytest.fixture()
def session_db(tmp_db_path):
    """Create a Database instance backed by a temp file."""
    return Database(db_path=tmp_db_path)


@pytest.fixture()
def task_db(tmp_db_path):
    """Create a TaskDatabase instance backed by a temp file."""
    return TaskDatabase(db_path=tmp_db_path)
