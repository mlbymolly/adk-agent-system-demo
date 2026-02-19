# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir -p /app/data
# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (frozen ensures lockfile is respected)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# Expose the API port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
