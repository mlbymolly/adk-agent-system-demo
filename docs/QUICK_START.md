# Quick Start Guide

Get up and running with the Weather, Date & Task Management Assistant in 5 minutes!

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Google API Key (Gemini)

## 1. Install Dependencies

```bash
uv sync
```

## 2. Configure API Key

Create or edit `.env` file:

```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here
```

## 3. Seed Sample Data (Optional)

Populate database with 15 sample tasks:

```bash
python seed_tasks.py
```

Expected output:

```text
Seeding tasks database...
Created task: Buy groceries (ID: 1)
Created task: Prepare presentation (ID: 2)
...
15/15 tasks created successfully!
```

## 4. Choose Your Interface

### Option A: Terminal Interface

```bash
python main.py
```

Try these commands:

```text
You: What's today's date?
You: How's the weather in Tokyo?
You: Create a task to buy milk tomorrow
You: Show me all my tasks
You: What tasks are overdue?
You: quit
```

### Option B: REST API Server

Start the server:

```bash
python api.py
```

The server will start at `http://localhost:8000`

Open your browser to `http://localhost:8000/docs` for interactive API documentation.

## 5. Test the API

### Create a Session

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice"}'
```

Save the `session_id` from the response.

### Chat with the Assistant

```bash
# Replace SESSION_ID with your actual session ID
curl -X POST http://localhost:8000/sessions/SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What tasks are due this week?"}'
```

### Create a Task (Direct API)

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team meeting",
    "description": "Weekly sync",
    "due_date": "2025-11-20",
    "priority": "high",
    "location": "London",
    "user_id": "alice"
  }'
```

### List All Tasks

```bash
curl http://localhost:8000/tasks
```

### Get Task Statistics

```bash
curl http://localhost:8000/tasks/query/statistics
```

### Get Overdue Tasks

```bash
curl http://localhost:8000/tasks/query/overdue
```

## 6. Explore the Features

### Natural Language Task Management

```bash
SESSION_ID="your_session_id"

# Create tasks
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a high priority task to prepare presentation for Friday in Paris"}'

# Query tasks
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me tasks in Paris and tell me the weather there"}'

# Get analytics
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me statistics about my tasks"}'
```

## Common Commands

### Terminal Interface

- `What's today's date?` - Get current date/time
- `How's the weather in [city]?` - Get weather
- `Create a task to [description]` - Create task
- `Show me my tasks` - List all tasks
- `What tasks are overdue?` - Find overdue tasks
- `Give me task statistics` - View analytics
- `quit` - Exit

### API Endpoints

**Sessions:**

- `POST /sessions` - Create session
- `POST /sessions/{id}/chat` - Chat
- `GET /sessions/{id}/history` - View history

**Tasks:**

- `POST /tasks` - Create
- `GET /tasks` - List (with filters)
- `PUT /tasks/{id}` - Update
- `DELETE /tasks/{id}` - Delete
- `POST /tasks/{id}/complete` - Complete

**Analytics:**

- `GET /tasks/query/overdue` - Overdue
- `GET /tasks/query/due-soon` - Upcoming
- `GET /tasks/query/statistics` - Stats
- `GET /tasks/query/search?q=term` - Search

## Troubleshooting

### "GOOGLE_API_KEY not found"

- Make sure `.env` file exists
- Check that `GOOGLE_API_KEY` is set correctly
- Restart the application

### "Task not found"

- Run `python seed_tasks.py` to create sample data
- Check task ID exists: `curl http://localhost:8000/tasks`

### Database Issues

- Delete `assistant.db` file
- Restart the application (tables will be recreated)
- Re-run seed script if needed

## Next Steps

- Read `README.md` for full overview
- Check `TASK_API_DOCS.md` for complete API reference
- See `API_README.md` for session management details
- Explore `http://localhost:8000/docs` for interactive API docs

## File Structure

```text
├── main.py              # Terminal interface
├── api.py               # REST API server
├── agents.py            # AI agents
├── tools.py             # Date/weather tools
├── task_tools.py        # Task management tools
├── database.py          # Session database
├── task_database.py     # Task database
├── seed_tasks.py        # Sample data generator
└── assistant.db         # SQLite database (auto-created)
```

## Example Python Script

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a session
response = requests.post(f"{BASE_URL}/sessions", json={"user_id": "alice"})
session_id = response.json()["session_id"]

# Create a task via agent
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/chat",
    json={"message": "Create a task to review code with high priority for tomorrow"}
)
print(response.json()["assistant_message"])

# Get task statistics
response = requests.get(f"{BASE_URL}/tasks/query/statistics?user_id=alice")
print(response.json())

# List overdue tasks
response = requests.get(f"{BASE_URL}/tasks/query/overdue?user_id=alice")
print(f"Overdue tasks: {len(response.json())}")
```

Happy task managing!
