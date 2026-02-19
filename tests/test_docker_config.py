"""Tests that validate Docker configuration files are correct and consistent."""

import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDockerfile:
    """Validate Dockerfile structure."""

    @pytest.fixture(autouse=True)
    def _read_dockerfile(self):
        with open(os.path.join(PROJECT_ROOT, "Dockerfile")) as f:
            self.content = f.read()
            self.lines = self.content.splitlines()

    def test_dockerfile_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "Dockerfile"))

    def test_base_image_is_python_slim(self):
        assert any("python:3.12-slim" in line for line in self.lines)

    def test_uv_is_installed(self):
        assert any("ghcr.io/astral-sh/uv" in line for line in self.lines)

    def test_copies_lockfile_before_source(self):
        lockfile_idx = next(
            i for i, l in enumerate(self.lines) if "pyproject.toml" in l and "COPY" in l
        )
        source_idx = next(
            i for i, l in enumerate(self.lines) if l.strip() == "COPY . ."
        )
        assert lockfile_idx < source_idx, "Lockfile should be copied before full source for layer caching"

    def test_uses_frozen_sync(self):
        assert any("--frozen" in line for line in self.lines)

    def test_no_dev_dependencies(self):
        sync_lines = [l for l in self.lines if "uv sync" in l]
        assert all("--no-dev" in l for l in sync_lines)

    def test_exposes_port_8000(self):
        assert any("EXPOSE 8000" in line for line in self.lines)

    def test_cmd_runs_uvicorn(self):
        assert any("uvicorn" in line and "CMD" in line for line in self.lines)

    def test_data_directory_created(self):
        assert any("mkdir" in line and "/app/data" in line for line in self.lines)


class TestDockerCompose:
    """Validate docker-compose.yml structure."""

    @pytest.fixture(autouse=True)
    def _read_compose(self):
        with open(os.path.join(PROJECT_ROOT, "docker-compose.yml")) as f:
            self.content = f.read()

    def test_compose_file_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "docker-compose.yml"))

    def test_maps_port_8000(self):
        assert "8000:8000" in self.content

    def test_uses_env_file(self):
        assert ".env" in self.content

    def test_sets_db_path(self):
        assert "DB_PATH=" in self.content
        assert "/app/data/" in self.content

    def test_has_volume(self):
        assert "app-data" in self.content

    def test_has_healthcheck(self):
        assert "healthcheck" in self.content
        assert "/health" in self.content


class TestDockerIgnore:
    """Validate .dockerignore excludes the right things."""

    @pytest.fixture(autouse=True)
    def _read_dockerignore(self):
        with open(os.path.join(PROJECT_ROOT, ".dockerignore")) as f:
            self.entries = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    def test_dockerignore_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, ".dockerignore"))

    def test_excludes_git(self):
        assert ".git" in self.entries

    def test_excludes_venv(self):
        assert ".venv" in self.entries

    def test_excludes_env_file(self):
        assert ".env" in self.entries

    def test_excludes_db_files(self):
        assert "*.db" in self.entries

    def test_excludes_pycache(self):
        assert "__pycache__" in self.entries


class TestEnvExample:
    """Validate .env.example exists and has required keys."""

    @pytest.fixture(autouse=True)
    def _read_env_example(self):
        path = os.path.join(PROJECT_ROOT, ".env.example")
        assert os.path.isfile(path), ".env.example must exist"
        with open(path) as f:
            self.content = f.read()

    def test_has_google_api_key(self):
        assert "GOOGLE_API_KEY" in self.content

    def test_has_vertexai_flag(self):
        assert "GOOGLE_GENAI_USE_VERTEXAI" in self.content

    def test_does_not_contain_real_key(self):
        for line in self.content.splitlines():
            if "GOOGLE_API_KEY" in line:
                value = line.split("=", 1)[1].strip()
                assert value in ("", "your_google_api_key_here"), \
                    "env.example should not contain a real API key"
