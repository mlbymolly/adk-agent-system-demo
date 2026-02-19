"""Task management endpoints."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from src.models.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.database.task_db import TaskDatabase

# Initialize router
router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Initialize database
task_db = TaskDatabase()


@router.post("", response_model=TaskResponse)
async def create_new_task(task: TaskCreate):
    """Create a new task."""
    created_task = task_db.create_task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        location=task.location,
        user_id=task.user_id
    )
    return TaskResponse(**created_task)


@router.get("", response_model=List[TaskResponse])
async def list_all_tasks(
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: Optional[int] = Query(50)
):
    """List all tasks with optional filters."""
    tasks = task_db.get_all_tasks(
        user_id=user_id,
        status=status,
        priority=priority,
        limit=limit
    )
    return [TaskResponse(**task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int):
    """Get a specific task by ID."""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_existing_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task."""
    updated_task = task_db.update_task(
        task_id=task_id,
        title=task_update.title,
        description=task_update.description,
        due_date=task_update.due_date,
        priority=task_update.priority,
        location=task_update.location,
        status=task_update.status
    )
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**updated_task)


@router.delete("/{task_id}")
async def delete_existing_task(task_id: int):
    """Delete a task."""
    deleted = task_db.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully", "task_id": task_id}


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete(task_id: int):
    """Mark a task as completed."""
    updated_task = task_db.update_task(task_id=task_id, status="completed")
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**updated_task)


# ==================== Analytics Endpoints ====================

@router.get("/query/overdue", response_model=List[TaskResponse], tags=["Tasks - Analytics"])
async def get_overdue(user_id: Optional[str] = Query(None)):
    """Get all overdue tasks."""
    tasks = task_db.get_overdue_tasks(user_id=user_id)
    return [TaskResponse(**task) for task in tasks]


@router.get("/query/due-soon", response_model=List[TaskResponse], tags=["Tasks - Analytics"])
async def get_due_soon(
    days: int = Query(7, description="Number of days to look ahead"),
    user_id: Optional[str] = Query(None)
):
    """Get tasks due within the next N days."""
    tasks = task_db.get_tasks_due_soon(days=days, user_id=user_id)
    return [TaskResponse(**task) for task in tasks]


@router.get("/query/statistics", tags=["Tasks - Analytics"])
async def get_statistics(user_id: Optional[str] = Query(None)):
    """Get task statistics and analytics."""
    stats = task_db.get_task_statistics(user_id=user_id)
    return stats


@router.get("/query/by-location", response_model=List[TaskResponse], tags=["Tasks - Analytics"])
async def get_by_location(
    location: str = Query(..., description="Location to search for"),
    user_id: Optional[str] = Query(None)
):
    """Get tasks for a specific location."""
    tasks = task_db.get_tasks_by_location(location=location, user_id=user_id)
    return [TaskResponse(**task) for task in tasks]


@router.get("/query/search", response_model=List[TaskResponse], tags=["Tasks - Analytics"])
async def search_for_tasks(
    q: str = Query(..., description="Search term"),
    user_id: Optional[str] = Query(None)
):
    """Search tasks by title or description."""
    tasks = task_db.search_tasks(search_term=q, user_id=user_id)
    return [TaskResponse(**task) for task in tasks]


@router.get("/query/date-range", response_model=List[TaskResponse], tags=["Tasks - Analytics"])
async def get_by_date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None)
):
    """Get tasks within a date range."""
    tasks = task_db.get_tasks_by_date_range(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )
    return [TaskResponse(**task) for task in tasks]
