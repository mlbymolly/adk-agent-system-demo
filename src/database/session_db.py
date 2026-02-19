"""Database models and utilities for storing sessions and message history."""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

DEFAULT_DB_PATH = os.getenv("DB_PATH", "assistant.db")


class Database:
    """SQLite database manager for sessions and messages."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                app_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_session(self, session_id: str, user_id: str, app_name: str) -> Dict:
        """Create a new session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, app_name)
            VALUES (?, ?, ?)
        """, (session_id, user_id, app_name))

        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "user_id": user_id,
            "app_name": app_name,
            "created_at": datetime.now().isoformat()
        }

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_sessions(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get all sessions, optionally filtered by user_id."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM sessions WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT * FROM sessions
                ORDER BY updated_at DESC
            """)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def add_message(self, session_id: str, role: str, content: str) -> Dict:
        """Add a message to a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Add message
        cursor.execute("""
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)
        """, (session_id, role, content))

        message_id = cursor.lastrowid

        # Update session updated_at
        cursor.execute("""
            UPDATE sessions SET updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))

        conn.commit()
        conn.close()

        return {
            "id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": datetime.now().isoformat()
        }

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get all messages for a session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if limit:
            cursor.execute("""
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (session_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete messages first
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

        # Delete session
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def clear_all_sessions(self) -> int:
        """Clear all sessions and messages. Returns count of deleted sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM messages")
        cursor.execute("DELETE FROM sessions")

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted
