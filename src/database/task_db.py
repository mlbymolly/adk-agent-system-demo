"""Task management database models and utilities."""

import os
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional
import json

DEFAULT_DB_PATH = os.getenv("DB_PATH", "assistant.db")


class TaskDatabase:
    """SQLite database manager for task management."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Create task tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date DATE,
                priority TEXT DEFAULT 'medium',
                location TEXT,
                status TEXT DEFAULT 'pending',
                weather_note TEXT,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)
        """)

        conn.commit()
        conn.close()

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: str = "medium",
        location: Optional[str] = None,
        status: str = "pending",
        weather_note: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Create a new task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tasks (title, description, due_date, priority, location, status, weather_note, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, due_date, priority, location, status, weather_note, user_id))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return self.get_task(task_id)

    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get task by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_all_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Get all tasks with optional filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY due_date ASC NULLS LAST, priority DESC, created_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        weather_note: Optional[str] = None
    ) -> Optional[Dict]:
        """Update an existing task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build dynamic update query
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if due_date is not None:
            updates.append("due_date = ?")
            params.append(due_date)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            # If status is completed, set completed_at
            if status == "completed":
                updates.append("completed_at = CURRENT_TIMESTAMP")
        if weather_note is not None:
            updates.append("weather_note = ?")
            params.append(weather_note)

        if not updates:
            conn.close()
            return self.get_task(task_id)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(task_id)

        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()

        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def get_tasks_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """Get tasks within a date range."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if start_date:
            query += " AND due_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND due_date <= ?"
            params.append(end_date)

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY due_date ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_overdue_tasks(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get all overdue tasks."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT * FROM tasks
            WHERE due_date < date('now')
            AND status != 'completed'
        """
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY due_date ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_tasks_due_soon(self, days: int = 7, user_id: Optional[str] = None) -> List[Dict]:
        """Get tasks due within the next N days."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT * FROM tasks
            WHERE due_date >= date('now')
            AND due_date <= date('now', '+' || ? || ' days')
            AND status != 'completed'
        """
        params = [days]

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY due_date ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_task_statistics(self, user_id: Optional[str] = None) -> Dict:
        """Get task statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total tasks
        query = "SELECT COUNT(*) as count FROM tasks"
        params = []
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)

        cursor.execute(query, params)
        stats["total_tasks"] = cursor.fetchone()[0]

        # Tasks by status
        query = "SELECT status, COUNT(*) as count FROM tasks"
        if user_id:
            query += " WHERE user_id = ?"
        query += " GROUP BY status"

        cursor.execute(query, params)
        stats["by_status"] = {row[0]: row[1] for row in cursor.fetchall()}

        # Tasks by priority
        query = "SELECT priority, COUNT(*) as count FROM tasks"
        if user_id:
            query += " WHERE user_id = ?"
        query += " GROUP BY priority"

        cursor.execute(query, params)
        stats["by_priority"] = {row[0]: row[1] for row in cursor.fetchall()}

        # Overdue tasks
        query = """
            SELECT COUNT(*) as count FROM tasks
            WHERE due_date < date('now')
            AND status != 'completed'
        """
        if user_id:
            query += " AND user_id = ?"

        cursor.execute(query, params)
        stats["overdue_count"] = cursor.fetchone()[0]

        # Due this week
        query = """
            SELECT COUNT(*) as count FROM tasks
            WHERE due_date >= date('now')
            AND due_date <= date('now', '+7 days')
            AND status != 'completed'
        """
        if user_id:
            query += " AND user_id = ?"

        cursor.execute(query, params)
        stats["due_this_week"] = cursor.fetchone()[0]

        conn.close()
        return stats

    def get_tasks_by_location(self, location: str, user_id: Optional[str] = None) -> List[Dict]:
        """Get all tasks for a specific location."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE location LIKE ?"
        params = [f"%{location}%"]

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY due_date ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_tasks(self, search_term: str, user_id: Optional[str] = None) -> List[Dict]:
        """Search tasks by title or description."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT * FROM tasks
            WHERE (title LIKE ? OR description LIKE ?)
        """
        params = [f"%{search_term}%", f"%{search_term}%"]

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY due_date ASC NULLS LAST"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
