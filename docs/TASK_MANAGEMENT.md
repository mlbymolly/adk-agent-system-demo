# Task Management API Documentation

Complete API documentation for the Task Management features of the Weather & Date Assistant.

## Table of Contents

- [Overview](#overview)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
  - [Basic CRUD Operations](#basic-crud-operations)
  - [Analytics & Queries](#analytics--queries)
- [Agent Integration](#agent-integration)
- [Usage Examples](#usage-examples)

## Overview

The Task Management system provides comprehensive CRUD operations and analytics for managing tasks with the following features:

- **Full CRUD**: Create, Read, Update, Delete tasks
- **Advanced Filtering**: Filter by status, priority, user, location
- **Analytics**: Statistics, overdue tasks, upcoming tasks
- **Date-based Queries**: Tasks by date range, due soon, overdue
- **Location Integration**: Tasks with location + weather data
- **AI Agent Integration**: Natural language task management

## Database Schema

### Tasks Table

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| title | TEXT | Task title (required) |
| description | TEXT | Detailed description (optional) |
| due_date | DATE | Due date in YYYY-MM-DD format (optional) |
| priority | TEXT | Priority: low, medium, high (default: medium) |
| location | TEXT | Associated location (optional) |
| status | TEXT | Status: pending, in_progress, completed (default: pending) |
| weather_note | TEXT | Weather-related notes (optional) |
| user_id | TEXT | User ID who owns the task |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| completed_at | TIMESTAMP | Completion timestamp (null if not completed) |

## API Endpoints

Base URL: `http://localhost:8000`

### Basic CRUD Operations

#### 1. Create Task

**POST /tasks**

Create a new task.

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Get milk, eggs, and bread",
    "due_date": "2025-11-20",
    "priority": "high",
    "location": "New York",
    "user_id": "alice"
  }'
```

**Request Body:**
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "due_date": "YYYY-MM-DD (optional)",
  "priority": "low|medium|high (optional, default: medium",
  "location": "string (optional)",
  "user_id": "string (optional, default: default)"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Get milk, eggs, and bread",
  "due_date": "2025-11-20",
  "priority": "high",
  "location": "New York",
  "status": "pending",
  "weather_note": null,
  "user_id": "alice",
  "created_at": "2025-11-14T21:00:00",
  "updated_at": "2025-11-14T21:00:00",
  "completed_at": null
}
```

#### 2. List Tasks

**GET /tasks**

List all tasks with optional filters.

```bash
# Get all tasks
curl http://localhost:8000/tasks

# Filter by user
curl "http://localhost:8000/tasks?user_id=alice"

# Filter by status
curl "http://localhost:8000/tasks?status=pending"

# Filter by priority
curl "http://localhost:8000/tasks?priority=high"

# Combine filters
curl "http://localhost:8000/tasks?user_id=alice&status=pending&priority=high&limit=10"
```

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `status` (optional): Filter by status (pending, in_progress, completed)
- `priority` (optional): Filter by priority (low, medium, high)
- `limit` (optional): Maximum number of results (default: 50)

**Response:** Array of task objects

#### 3. Get Task by ID

**GET /tasks/{task_id}**

Get details of a specific task.

```bash
curl http://localhost:8000/tasks/1
```

**Response:** Single task object

#### 4. Update Task

**PUT /tasks/{task_id}**

Update an existing task.

```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "medium"
  }'
```

**Request Body:** (all fields optional)
```json
{
  "title": "string",
  "description": "string",
  "due_date": "YYYY-MM-DD",
  "priority": "low|medium|high",
  "location": "string",
  "status": "pending|in_progress|completed"
}
```

#### 5. Delete Task

**DELETE /tasks/{task_id}**

Delete a task permanently.

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

**Response:**
```json
{
  "message": "Task deleted successfully",
  "task_id": 1
}
```

#### 6. Complete Task

**POST /tasks/{task_id}/complete**

Mark a task as completed (shortcut for updating status).

```bash
curl -X POST http://localhost:8000/tasks/1/complete
```

**Response:** Updated task object with `status: "completed"` and `completed_at` timestamp

### Analytics & Queries

#### 1. Get Overdue Tasks

**GET /tasks/query/overdue**

Get all tasks that are past their due date and not completed.

```bash
# All overdue tasks
curl http://localhost:8000/tasks/query/overdue

# Overdue tasks for specific user
curl "http://localhost:8000/tasks/query/overdue?user_id=alice"
```

#### 2. Get Tasks Due Soon

**GET /tasks/query/due-soon**

Get tasks due within the next N days.

```bash
# Tasks due in next 7 days (default)
curl http://localhost:8000/tasks/query/due-soon

# Tasks due in next 3 days
curl "http://localhost:8000/tasks/query/due-soon?days=3"

# For specific user
curl "http://localhost:8000/tasks/query/due-soon?days=7&user_id=alice"
```

**Query Parameters:**
- `days` (optional): Number of days to look ahead (default: 7)
- `user_id` (optional): Filter by user ID

#### 3. Get Task Statistics

**GET /tasks/query/statistics**

Get comprehensive task statistics and analytics.

```bash
# All tasks statistics
curl http://localhost:8000/tasks/query/statistics

# Statistics for specific user
curl "http://localhost:8000/tasks/query/statistics?user_id=alice"
```

**Response:**
```json
{
  "total_tasks": 15,
  "by_status": {
    "pending": 8,
    "in_progress": 4,
    "completed": 3
  },
  "by_priority": {
    "low": 3,
    "medium": 7,
    "high": 5
  },
  "overdue_count": 2,
  "due_this_week": 5
}
```

#### 4. Get Tasks by Location

**GET /tasks/query/by-location**

Get all tasks for a specific location.

```bash
curl "http://localhost:8000/tasks/query/by-location?location=New%20York"

# With user filter
curl "http://localhost:8000/tasks/query/by-location?location=Tokyo&user_id=alice"
```

**Query Parameters:**
- `location` (required): Location to search for
- `user_id` (optional): Filter by user ID

#### 5. Search Tasks

**GET /tasks/query/search**

Search tasks by title or description.

```bash
curl "http://localhost:8000/tasks/query/search?q=groceries"

# With user filter
curl "http://localhost:8000/tasks/query/search?q=meeting&user_id=bob"
```

**Query Parameters:**
- `q` (required): Search term
- `user_id` (optional): Filter by user ID

#### 6. Get Tasks by Date Range

**GET /tasks/query/date-range**

Get tasks within a specific date range.

```bash
curl "http://localhost:8000/tasks/query/date-range?start_date=2025-11-15&end_date=2025-11-30"

# With user filter
curl "http://localhost:8000/tasks/query/date-range?start_date=2025-11-15&end_date=2025-11-30&user_id=alice"
```

**Query Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `user_id` (optional): Filter by user ID

## Agent Integration

The Task Management Agent can be accessed via the chat interface at:

**POST /sessions/{session_id}/chat**

### Example Agent Queries

```bash
# Create session first
SESSION_ID=$(curl -s -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice"}' | jq -r '.session_id')

# Create a task via agent
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to prepare presentation for next Friday with high priority"}'

# List tasks via agent
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all my pending tasks"}'

# Get overdue tasks
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tasks are overdue?"}'

# Get statistics
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me task statistics"}'

# Tasks by location with weather
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me tasks in Tokyo and tell me the weather there"}'

# Complete a task
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark task 1 as completed"}'

# Search tasks
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find all tasks related to presentations"}'
```

## Seeding Sample Data

Run the seed script to populate the database with sample tasks:

```bash
python seed_tasks.py
```

This creates 15 sample tasks with various:
- Due dates (past, present, future)
- Priorities (low, medium, high)
- Statuses (pending, in_progress, completed)
- Locations (New York, Tokyo, Paris, etc.)
- Users (alice, bob)

## Python Client Examples

### Create and Manage Tasks

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a task
response = requests.post(
    f"{BASE_URL}/tasks",
    json={
        "title": "Team meeting",
        "description": "Weekly sync with the team",
        "due_date": "2025-11-20",
        "priority": "medium",
        "location": "London",
        "user_id": "alice"
    }
)
task = response.json()
task_id = task["id"]
print(f"Created task: {task['title']} (ID: {task_id})")

# List all tasks
response = requests.get(f"{BASE_URL}/tasks")
tasks = response.json()
print(f"Total tasks: {len(tasks)}")

# Get overdue tasks
response = requests.get(f"{BASE_URL}/tasks/query/overdue?user_id=alice")
overdue = response.json()
print(f"Overdue tasks: {len(overdue)}")

# Get tasks due soon
response = requests.get(f"{BASE_URL}/tasks/query/due-soon?days=7&user_id=alice")
upcoming = response.json()
print(f"Tasks due this week: {len(upcoming)}")

# Get statistics
response = requests.get(f"{BASE_URL}/tasks/query/statistics?user_id=alice")
stats = response.json()
print(f"Statistics: {stats}")

# Update task
response = requests.put(
    f"{BASE_URL}/tasks/{task_id}",
    json={"status": "in_progress", "priority": "high"}
)
updated_task = response.json()
print(f"Updated task status: {updated_task['status']}")

# Complete task
response = requests.post(f"{BASE_URL}/tasks/{task_id}/complete")
completed_task = response.json()
print(f"Task completed: {completed_task['title']}")

# Search tasks
response = requests.get(f"{BASE_URL}/tasks/query/search?q=meeting&user_id=alice")
search_results = response.json()
print(f"Found {len(search_results)} tasks matching 'meeting'")

# Get tasks by location
response = requests.get(f"{BASE_URL}/tasks/query/by-location?location=London")
location_tasks = response.json()
print(f"Tasks in London: {len(location_tasks)}")

# Delete task
response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
result = response.json()
print(result["message"])
```

### Combined with Agent Chat

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a session
response = requests.post(f"{BASE_URL}/sessions", json={"user_id": "alice"})
session = response.json()
session_id = session["session_id"]

# Use natural language to manage tasks
queries = [
    "Create a task to buy groceries tomorrow with high priority in New York",
    "What's the weather in New York?",
    "Show me all my pending tasks",
    "Which tasks are overdue?",
    "Give me statistics about my tasks",
    "Mark task 1 as completed"
]

for query in queries:
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/chat",
        json={"message": query}
    )
    result = response.json()
    print(f"User: {query}")
    print(f"Assistant: {result['assistant_message']}\n")
```

## Best Practices

1. **Date Format**: Always use `YYYY-MM-DD` format for dates
2. **User IDs**: Assign meaningful user IDs for multi-user scenarios
3. **Priorities**: Use `high` for urgent tasks, `medium` for normal, `low` for optional
4. **Locations**: Be specific with locations for better weather integration
5. **Descriptions**: Provide detailed descriptions for better searchability
6. **Status Updates**: Keep task status updated for accurate analytics

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `404` - Task/Resource not found
- `422` - Validation error (invalid date format, priority, etc.)
- `500` - Internal server error

Example error response:
```json
{
  "detail": "Task not found"
}
```

## Notes

- Tasks are stored persistently in SQLite (`assistant.db`)
- Completed tasks are timestamped automatically
- All queries support optional user filtering for multi-tenant scenarios
- The agent can combine task management with weather and date information
- Statistics are calculated in real-time from the database
