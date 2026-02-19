"""Pydantic models for API request/response validation."""

from typing import Optional, List
from pydantic import BaseModel


# ==================== Session Models ====================

class CreateSessionRequest(BaseModel):
    """Request model for creating a new session."""
    user_id: Optional[str] = None


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""
    session_id: str
    user_id: str
    app_name: str
    created_at: str


class Session(BaseModel):
    """Session model with full details."""
    session_id: str
    user_id: str
    app_name: str
    created_at: str
    updated_at: str


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: str


class Message(BaseModel):
    """Individual message model."""
    id: int
    session_id: str
    role: str
    content: str
    created_at: str


class HistoryResponse(BaseModel):
    """Response model for conversation history."""
    session_id: str
    messages: List[Message]


# ==================== Task Models ====================

class TaskCreate(BaseModel):
    """Request model for creating a new task."""
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "medium"
    location: Optional[str] = None
    user_id: Optional[str] = "default"


class TaskUpdate(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None


class TaskResponse(BaseModel):
    """Response model for task data."""
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[str]
    priority: str
    location: Optional[str]
    status: str
    weather_note: Optional[str]
    user_id: Optional[str]
    created_at: str
    updated_at: str
    completed_at: Optional[str]
