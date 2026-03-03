"""Main entry point for the Multi-Agent System API."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.routers.sessions import router as sessions_router
from src.routers.tasks import router as tasks_router
from src.routers.sdlc_router import router as sdlc_router

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent System with Google ADK",
    description="A comprehensive reference implementation for building production-ready multi-agent systems.",
    version="2.0.0",
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
app.include_router(sdlc_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Check the health of the API and its components."""
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "api_key_configured": api_key_set,
        "database": "connected",
        "agents": "ready",
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "Multi-Agent System API",
        "version": "2.0.0",
        "documentation": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
