"""Task management tools for AI agents."""

from datetime import datetime, date, timedelta
from typing import Optional, List
import json
from src.database.task_db import TaskDatabase

# Initialize task database
task_db = TaskDatabase()


def create_task(
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str = "medium",
    location: str = "",
    user_id: str = "default"
) -> str:
    """Create a new task.

    Args:
        title: Task title (required)
        description: Detailed description of the task
        due_date: Due date in YYYY-MM-DD format
        priority: Priority level (low, medium, high)
        location: Location associated with the task
        user_id: User ID who owns the task

    Returns:
        str: JSON string with created task details
    """
    # Validate priority
    if priority not in ["low", "medium", "high"]:
        return json.dumps({"error": "Priority must be low, medium, or high"})

    # Validate date format if provided
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({"error": "Date must be in YYYY-MM-DD format"})

    task = task_db.create_task(
        title=title,
        description=description or None,
        due_date=due_date or None,
        priority=priority,
        location=location or None,
        user_id=user_id
    )

    return json.dumps(task, indent=2)


def get_task(task_id: int) -> str:
    """Get a specific task by ID.

    Args:
        task_id: The ID of the task to retrieve

    Returns:
        str: JSON string with task details or error message
    """
    task = task_db.get_task(task_id)

    if not task:
        return json.dumps({"error": f"Task with ID {task_id} not found"})

    return json.dumps(task, indent=2)


def list_tasks(
    status: str = "",
    priority: str = "",
    limit: int = 50,
    user_id: str = "default"
) -> str:
    """List all tasks with optional filters.

    Args:
        status: Filter by status (pending, in_progress, completed)
        priority: Filter by priority (low, medium, high)
        limit: Maximum number of tasks to return
        user_id: Filter by user ID

    Returns:
        str: JSON string with list of tasks
    """
    tasks = task_db.get_all_tasks(
        user_id=user_id,
        status=status or None,
        priority=priority or None,
        limit=limit
    )

    return json.dumps({
        "count": len(tasks),
        "tasks": tasks
    }, indent=2)


def update_task(
    task_id: int,
    title: str = "",
    description: str = "",
    due_date: str = "",
    priority: str = "",
    location: str = "",
    status: str = ""
) -> str:
    """Update an existing task.

    Args:
        task_id: The ID of the task to update
        title: New title for the task
        description: New description
        due_date: New due date in YYYY-MM-DD format
        priority: New priority (low, medium, high)
        location: New location
        status: New status (pending, in_progress, completed)

    Returns:
        str: JSON string with updated task details
    """
    # Validate inputs
    if priority and priority not in ["low", "medium", "high"]:
        return json.dumps({"error": "Priority must be low, medium, or high"})

    if status and status not in ["pending", "in_progress", "completed"]:
        return json.dumps({"error": "Status must be pending, in_progress, or completed"})

    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({"error": "Date must be in YYYY-MM-DD format"})

    # Update only provided fields
    task = task_db.update_task(
        task_id=task_id,
        title=title or None,
        description=description or None,
        due_date=due_date or None,
        priority=priority or None,
        location=location or None,
        status=status or None
    )

    if not task:
        return json.dumps({"error": f"Task with ID {task_id} not found"})

    return json.dumps(task, indent=2)


def delete_task(task_id: int) -> str:
    """Delete a task.

    Args:
        task_id: The ID of the task to delete

    Returns:
        str: JSON string with success or error message
    """
    deleted = task_db.delete_task(task_id)

    if deleted:
        return json.dumps({"success": True, "message": f"Task {task_id} deleted successfully"})
    else:
        return json.dumps({"success": False, "error": f"Task with ID {task_id} not found"})


def get_overdue_tasks(user_id: str = "default") -> str:
    """Get all overdue tasks.

    Args:
        user_id: Filter by user ID

    Returns:
        str: JSON string with list of overdue tasks
    """
    tasks = task_db.get_overdue_tasks(user_id=user_id)

    return json.dumps({
        "count": len(tasks),
        "overdue_tasks": tasks
    }, indent=2)


def get_tasks_due_soon(days: int = 7, user_id: str = "default") -> str:
    """Get tasks due within the next N days.

    Args:
        days: Number of days to look ahead
        user_id: Filter by user ID

    Returns:
        str: JSON string with list of upcoming tasks
    """
    tasks = task_db.get_tasks_due_soon(days=days, user_id=user_id)

    return json.dumps({
        "count": len(tasks),
        "days_ahead": days,
        "upcoming_tasks": tasks
    }, indent=2)


def get_task_statistics(user_id: str = "default") -> str:
    """Get task statistics and analytics.

    Args:
        user_id: Filter by user ID

    Returns:
        str: JSON string with task statistics
    """
    stats = task_db.get_task_statistics(user_id=user_id)

    return json.dumps(stats, indent=2)


def get_tasks_by_location(location: str, user_id: str = "default") -> str:
    """Get all tasks for a specific location.

    Args:
        location: The location to search for
        user_id: Filter by user ID

    Returns:
        str: JSON string with list of tasks for the location
    """
    tasks = task_db.get_tasks_by_location(location=location, user_id=user_id)

    return json.dumps({
        "count": len(tasks),
        "location": location,
        "tasks": tasks
    }, indent=2)


def search_tasks(search_term: str, user_id: str = "default") -> str:
    """Search tasks by title or description.

    Args:
        search_term: The term to search for
        user_id: Filter by user ID

    Returns:
        str: JSON string with matching tasks
    """
    tasks = task_db.search_tasks(search_term=search_term, user_id=user_id)

    return json.dumps({
        "count": len(tasks),
        "search_term": search_term,
        "tasks": tasks
    }, indent=2)


def get_tasks_by_date_range(
    start_date: str,
    end_date: str,
    user_id: str = "default"
) -> str:
    """Get tasks within a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_id: Filter by user ID

    Returns:
        str: JSON string with tasks in the date range
    """
    # Validate dates
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return json.dumps({"error": "Dates must be in YYYY-MM-DD format"})

    tasks = task_db.get_tasks_by_date_range(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id
    )

    return json.dumps({
        "count": len(tasks),
        "start_date": start_date,
        "end_date": end_date,
        "tasks": tasks
    }, indent=2)


def complete_task(task_id: int) -> str:
    """Mark a task as completed.

    Args:
        task_id: The ID of the task to complete

    Returns:
        str: JSON string with updated task details
    """
    task = task_db.update_task(task_id=task_id, status="completed")

    if not task:
        return json.dumps({"error": f"Task with ID {task_id} not found"})

    return json.dumps({
        "success": True,
        "message": f"Task {task_id} marked as completed",
        "task": task
    }, indent=2)
