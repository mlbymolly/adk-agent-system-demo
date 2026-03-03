"""SDLC Management endpoints."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from google.genai import types

from src.agents.sdlc_agents import sdlc_coordinator

# Initialize router
router = APIRouter(prefix="/sdlc", tags=["SDLC"])

# App configuration
APP_NAME = "sdlc_system"

class SDLCChatRequest(BaseModel):
    """Request model for SDLC chat messages."""
    session_id: str
    message: str
    user_id: str = "default_sdlc_user"

class SDLCChatResponse(BaseModel):
    """Response model for SDLC chat interactions."""
    session_id: str
    user_message: str
    assistant_message: str

@router.post("/chat", response_model=SDLCChatResponse)
async def sdlc_chat(request: SDLCChatRequest):
    """Send a message to the SDLC coordinator and get a response."""

    # Ensure session exists in runner
    runner = InMemoryRunner(app_name=APP_NAME, agent=sdlc_coordinator)

    try:
        await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=request.session_id,
        )
    except Exception:
        # Session might already exist
        pass

    # Get agent response
    events = runner.run_async(
        user_id=request.user_id,
        session_id=request.session_id,
        new_message=types.Content(
            parts=[types.Part(text=request.message)],
            role="user"
        ),
    )

    # Collect response
    response_text = ""
    async for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    return SDLCChatResponse(
        session_id=request.session_id,
        user_message=request.message,
        assistant_message=response_text.strip()
    )

@router.get("/issues")
def get_issues():
    """Fetch all issues (Mock)."""
    return {"message": "List of issues", "issues": []}

@router.post("/issues")
def create_issue(issue: Dict[str, Any]):
    """Create a new issue (Mock)."""
    return {"message": "Issue created", "issue": issue}

@router.get("/pull-requests")
def get_pull_requests():
    """Fetch all pull requests (Mock)."""
    return {"message": "List of pull requests", "pull_requests": []}

@router.post("/pull-requests")
def create_pull_request(pr: Dict[str, Any]):
    """Create a new pull request (Mock)."""
    return {"message": "Pull request created", "pull_request": pr}

@router.get("/code-reviews")
def get_code_reviews():
    """Fetch all code reviews (Mock)."""
    return {"message": "List of code reviews", "reviews": []}

@router.get("/test-cases")
def get_test_cases():
    """Fetch all test cases (Mock)."""
    return {"message": "List of test cases", "test_cases": []}

@router.get("/deployments")
def get_deployments():
    """Fetch all deployments (Mock)."""
    return {"message": "List of deployments", "deployments": []}

@router.get("/performance")
def get_performance_metrics():
    """Fetch performance monitoring metrics (Mock)."""
    return {"message": "Performance metrics", "metrics": {}}
