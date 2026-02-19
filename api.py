"""FastAPI application for Weather, Date & Task Management Assistant.

This is the main entry point for the multi-agent system API server.
Clean architecture with routers and models separated.
"""

import os
import warnings
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import sessions_router, tasks_router

# Suppress warnings and logging
warnings.filterwarnings('ignore')
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('google.adk').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Weather, Date & Task Management Assistant API",
    description="A comprehensive multi-agent system for weather information, date queries, and task management with CRUD operations and analytics",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions_router)
app.include_router(tasks_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Weather, Date & Task Management Assistant API",
        "version": "2.0.0",
        "description": "Multi-agent system for task management, weather, and date queries",
        "documentation": "/docs",
        "endpoints": {
            "sessions": {
                "create": "POST /sessions",
                "list": "GET /sessions",
                "get": "GET /sessions/{session_id}",
                "chat": "POST /sessions/{session_id}/chat",
                "history": "GET /sessions/{session_id}/history",
                "delete": "DELETE /sessions/{session_id}"
            },
            "tasks": {
                "create": "POST /tasks",
                "list": "GET /tasks",
                "get": "GET /tasks/{task_id}",
                "update": "PUT /tasks/{task_id}",
                "delete": "DELETE /tasks/{task_id}",
                "complete": "POST /tasks/{task_id}/complete"
            },
            "analytics": {
                "overdue": "GET /tasks/query/overdue",
                "due_soon": "GET /tasks/query/due-soon",
                "statistics": "GET /tasks/query/statistics",
                "by_location": "GET /tasks/query/by-location",
                "search": "GET /tasks/query/search",
                "date_range": "GET /tasks/query/date-range"
            }
        }
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint."""
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "api_key_configured": api_key_set,
        "database": "connected",
        "agents": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
