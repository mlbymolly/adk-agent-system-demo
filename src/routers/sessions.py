"""Session and chat management endpoints."""

import uuid
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from google.adk.runners import InMemoryRunner
from google.genai import types

from src.models.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    Session,
    ChatRequest,
    ChatResponse,
    Message,
    HistoryResponse
)
from src.database.session_db import Database
from src.agents import coordinator_agent

# Initialize router
router = APIRouter(prefix="/sessions", tags=["Sessions"])

# Initialize database
db = Database()

# App configuration
APP_NAME = "weather_date_assistant"


@router.post("", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session."""
    # Generate IDs
    user_id = request.user_id or f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:12]}"

    # Create session in database
    session = db.create_session(session_id, user_id, APP_NAME)

    # Create session in ADK runner
    runner = InMemoryRunner(app_name=APP_NAME, agent=coordinator_agent)
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    return CreateSessionResponse(**session)


@router.get("", response_model=List[Session])
async def list_sessions(user_id: Optional[str] = Query(None)):
    """List all sessions, optionally filtered by user_id."""
    sessions = db.get_all_sessions(user_id)
    return [Session(**session) for session in sessions]


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get a specific session by ID."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return Session(**session)


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat(session_id: str, request: ChatRequest):
    """Send a message to the assistant and get a response."""
    from datetime import datetime

    # Verify session exists
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save user message to database
    db.add_message(session_id, "user", request.message)

    # Create runner and send message to agent
    runner = InMemoryRunner(app_name=APP_NAME, agent=coordinator_agent)

    # Ensure session exists in runner
    try:
        await runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=session["user_id"],
            session_id=session_id,
        )
    except:
        # Session might already exist, that's okay
        pass

    # Get agent response
    events = runner.run_async(
        user_id=session["user_id"],
        session_id=session_id,
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

    # Save assistant message to database
    if response_text.strip():
        db.add_message(session_id, "assistant", response_text.strip())

    return ChatResponse(
        session_id=session_id,
        user_message=request.message,
        assistant_message=response_text.strip(),
        timestamp=datetime.now().isoformat()
    )


@router.get("/{session_id}/history", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    limit: Optional[int] = Query(None, description="Limit number of messages")
):
    """Get chat history for a session."""
    # Verify session exists
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get messages
    messages = db.get_messages(session_id, limit)

    return HistoryResponse(
        session_id=session_id,
        messages=[Message(**msg) for msg in messages]
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages."""
    deleted = db.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session deleted successfully", "session_id": session_id}


@router.delete("")
async def clear_all_sessions():
    """Clear all sessions and messages."""
    count = db.clear_all_sessions()
    return {"message": f"Cleared {count} sessions"}
