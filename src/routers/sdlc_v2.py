from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid
from src.database.sdlc_db import SDLCDatabase
from src.services.sdlc_orchestrator import SDLCOrchestrator
from src.tools.repo_tools import clone_repository

router = APIRouter(prefix="/sdlc/v2", tags=["SDLC v2"])
db = SDLCDatabase()
orchestrator = SDLCOrchestrator()

class ProjectCreate(BaseModel):
    name: str
    repo_url: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    repo_url: str
    status: str

@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, background_tasks: BackgroundTasks):
    project_id = str(uuid.uuid4())[:8]

    # 1. Store in DB
    db.create_project(project_id, project.name, project.repo_url)

    # 2. Clone repo in background
    background_tasks.add_task(clone_repository, project.repo_url, project_id)

    return {
        "id": project_id,
        "name": project.name,
        "repo_url": project.repo_url,
        "status": "initializing"
    }

@router.post("/projects/{project_id}/plan")
async def generate_plan(project_id: str):
    # This would call the PlannerAgent
    # For now, simulate plan generation
    plan_content = "Migrate SQLAlchemy 1.x to 2.x\n1. Update requirements\n2. Refactor models\n3. Update sessions"
    plan_id = db.create_plan(project_id, plan_content)

    return {"plan_id": plan_id, "content": plan_content}

@router.post("/projects/{project_id}/approve")
async def approve_and_run(project_id: str, background_tasks: BackgroundTasks):
    # 1. In a real system, this would trigger the DAG decomposition
    # 2. Add mock tasks for demonstration
    db.add_dag_task("task1", project_id, "Update requirements.txt", "Bump sqlalchemy version", [])
    db.add_dag_task("task2", project_id, "Refactor User Model", "Update to DeclarativeBase", ["task1"])
    db.add_dag_task("task3", project_id, "Refactor Post Model", "Update to DeclarativeBase", ["task1"])
    db.add_dag_task("task4", project_id, "Verify Changes", "Run test suite", ["task2", "task3"])

    # 3. Start DAG execution in background
    background_tasks.add_task(orchestrator.run_dag, project_id)

    return {"status": "started", "message": "DAG execution initiated"}

@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str):
    tasks = db.get_project_tasks(project_id)
    return {"tasks": tasks}
