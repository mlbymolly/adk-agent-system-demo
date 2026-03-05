import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

DEFAULT_DB_PATH = os.getenv("DB_PATH", "assistant.db")

class SDLCDatabase:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdlc_projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                repo_url TEXT NOT NULL,
                workspace_path TEXT,
                status TEXT DEFAULT 'initialized',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Implementation Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS implementation_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                plan_content TEXT NOT NULL,
                status TEXT DEFAULT 'pending_approval',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES sdlc_projects (id)
            )
        """)

        # DAG Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dag_tasks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                dependencies TEXT, -- JSON list of task IDs
                status TEXT DEFAULT 'pending', -- pending, in_progress, completed, failed
                assigned_agent TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES sdlc_projects (id)
            )
        """)

        # Pull Requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdlc_pull_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                branch_name TEXT NOT NULL,
                pr_url TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES sdlc_projects (id)
            )
        """)

        conn.commit()
        conn.close()

    def create_project(self, project_id: str, name: str, repo_url: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sdlc_projects (id, name, repo_url) VALUES (?, ?, ?)",
            (project_id, name, repo_url)
        )
        conn.commit()
        conn.close()
        return {"id": project_id, "name": name, "repo_url": repo_url}

    def create_plan(self, project_id: str, plan_content: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO implementation_plans (project_id, plan_content) VALUES (?, ?)",
            (project_id, plan_content)
        )
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id

    def add_dag_task(self, task_id: str, project_id: str, title: str, description: str, dependencies: List[str]) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dag_tasks (id, project_id, title, description, dependencies) VALUES (?, ?, ?, ?, ?)",
            (task_id, project_id, title, description, json.dumps(dependencies))
        )
        conn.commit()
        conn.close()
        return task_id

    def update_task_status(self, task_id: str, status: str, result: str = None, error: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE dag_tasks SET status = ?, result = ?, error = ? WHERE id = ?",
            (status, result, error, task_id)
        )
        conn.commit()
        conn.close()

    def get_project_tasks(self, project_id: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dag_tasks WHERE project_id = ?", (project_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
