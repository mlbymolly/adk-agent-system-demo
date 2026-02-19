# Weather & Date Assistant - FastAPI Documentation

A FastAPI-based REST API for the Weather & Date Assistant with SQLite session and message history storage.

## Features

- Create and manage chat sessions
- Persistent message history storage in SQLite
- RESTful API endpoints for all operations
- Session-based conversation tracking
- Multi-user support

## Installation

1. Install dependencies:

```bash
uv sync
```

2. Ensure your `.env` file contains your Google API key:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key_here
```

## Running the API Server

Start the FastAPI server:

```bash
python api.py
```

Or using uvicorn directly:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

Interactive API documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Root Information

**GET /** - Get API information and available endpoints

```bash
curl http://localhost:8000/
```

### Health Check

**GET /health** - Check API health status

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "database": "connected"
}
```

### Session Management

#### Create a New Session

**POST /sessions** - Create a new chat session

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice"}'
```

Response:
```json
{
  "session_id": "session_abc123",
  "user_id": "alice",
  "app_name": "weather_date_assistant",
  "created_at": "2025-11-14T21:00:00"
}
```

Note: `user_id` is optional. If not provided, a random user ID will be generated.

#### List All Sessions

**GET /sessions** - List all sessions (optionally filter by user_id)

```bash
# Get all sessions
curl http://localhost:8000/sessions

# Filter by user_id
curl "http://localhost:8000/sessions?user_id=alice"
```

Response:
```json
[
  {
    "session_id": "session_abc123",
    "user_id": "alice",
    "app_name": "weather_date_assistant",
    "created_at": "2025-11-14T21:00:00",
    "updated_at": "2025-11-14T21:05:00"
  }
]
```

#### Get Specific Session

**GET /sessions/{session_id}** - Get details of a specific session

```bash
curl http://localhost:8000/sessions/session_abc123
```

Response:
```json
{
  "session_id": "session_abc123",
  "user_id": "alice",
  "app_name": "weather_date_assistant",
  "created_at": "2025-11-14T21:00:00",
  "updated_at": "2025-11-14T21:05:00"
}
```

#### Delete Session

**DELETE /sessions/{session_id}** - Delete a session and all its messages

```bash
curl -X DELETE http://localhost:8000/sessions/session_abc123
```

Response:
```json
{
  "message": "Session deleted successfully",
  "session_id": "session_abc123"
}
```

#### Clear All Sessions

**DELETE /sessions** - Delete all sessions and messages

```bash
curl -X DELETE http://localhost:8000/sessions
```

Response:
```json
{
  "message": "Cleared 5 sessions"
}
```

### Chat Operations

#### Send a Message

**POST /sessions/{session_id}/chat** - Send a message and get response

```bash
curl -X POST http://localhost:8000/sessions/session_abc123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is today'\''s date?"}'
```

Response:
```json
{
  "session_id": "session_abc123",
  "user_message": "What is today's date?",
  "assistant_message": "Today is Thursday, November 14, 2025 at 09:00 PM.",
  "timestamp": "2025-11-14T21:00:00"
}
```

#### Get Chat History

**GET /sessions/{session_id}/history** - Get all messages in a session

```bash
# Get all messages
curl http://localhost:8000/sessions/session_abc123/history

# Limit to last 10 messages
curl "http://localhost:8000/sessions/session_abc123/history?limit=10"
```

Response:
```json
{
  "session_id": "session_abc123",
  "messages": [
    {
      "id": 1,
      "session_id": "session_abc123",
      "role": "user",
      "content": "What is today's date?",
      "created_at": "2025-11-14T21:00:00"
    },
    {
      "id": 2,
      "session_id": "session_abc123",
      "role": "assistant",
      "content": "Today is Thursday, November 14, 2025 at 09:00 PM.",
      "created_at": "2025-11-14T21:00:01"
    }
  ]
}
```

## Example Usage Flow

### 1. Create a session

```bash
SESSION_ID=$(curl -s -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice"}' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
```

### 2. Send a message about the date

```bash
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What day is it today?"}'
```

### 3. Ask about the weather

```bash
curl -X POST http://localhost:8000/sessions/$SESSION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How is the weather in Paris?"}'
```

### 4. View chat history

```bash
curl http://localhost:8000/sessions/$SESSION_ID/history | jq
```

### 5. List all sessions

```bash
curl http://localhost:8000/sessions | jq
```

## Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Create a session
response = requests.post(f"{BASE_URL}/sessions", json={"user_id": "alice"})
session = response.json()
session_id = session["session_id"]
print(f"Created session: {session_id}")

# Send a message
response = requests.post(
    f"{BASE_URL}/sessions/{session_id}/chat",
    json={"message": "What's the weather in Tokyo?"}
)
chat = response.json()
print(f"User: {chat['user_message']}")
print(f"Assistant: {chat['assistant_message']}")

# Get history
response = requests.get(f"{BASE_URL}/sessions/{session_id}/history")
history = response.json()
print(f"Total messages: {len(history['messages'])}")

# List all sessions
response = requests.get(f"{BASE_URL}/sessions")
sessions = response.json()
print(f"Total sessions: {len(sessions)}")
```

## Database

The API uses SQLite to store:
- **Sessions**: session_id, user_id, app_name, timestamps
- **Messages**: message content, role (user/assistant), timestamps

Database file: `assistant.db` (created automatically)

## Project Structure

```
adk-demo/
├── api.py              # FastAPI application
├── database.py         # SQLite database utilities
├── agents.py           # Agent definitions
├── tools.py            # Custom tool functions
├── main.py             # Terminal CLI version
├── pyproject.toml      # Python dependencies (uv)
├── .env                # Environment variables
├── assistant.db        # SQLite database (auto-created)
├── README.md          # Terminal version docs
└── API_README.md      # This file
```

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `404` - Session not found
- `500` - Internal server error

Example error response:
```json
{
  "detail": "Session not found"
}
```

## CORS

CORS is enabled for all origins. In production, you should restrict this to specific domains.

## Notes

- Each session maintains its own conversation context
- Messages are stored persistently in SQLite
- The weather data is currently simulated (mock data)
- Sessions can be accessed by multiple concurrent requests
- The API supports multiple users simultaneously
