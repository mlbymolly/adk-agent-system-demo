import asyncio
import networkx as nx
from typing import List, Dict, Any
from src.database.sdlc_db import SDLCDatabase
from src.agents.sdlc_v2_agents import coder_agent, reviewer_agent

class SDLCOrchestrator:
    def __init__(self):
        self.db = SDLCDatabase()

    async def run_dag(self, project_id: str):
        """Runs the DAG of tasks for a project in parallel where possible."""
        tasks = self.db.get_project_tasks(project_id)

        # Build networkx graph
        dag = nx.DiGraph()
        task_map = {}

        for task in tasks:
            task_id = task['id']
            task_map[task_id] = task
            dag.add_node(task_id)
            import json
            deps = json.loads(task['dependencies'])
            for dep in deps:
                dag.add_edge(dep, task_id)

        if not nx.is_directed_acyclic_graph(dag):
            raise ValueError("The task dependencies do not form a DAG!")

        # Track completed tasks
        completed_tasks = set()
        running_tasks = {}

        while len(completed_tasks) < len(tasks):
            # Find tasks that are ready (all dependencies completed)
            ready_tasks = [
                tid for tid in dag.nodes
                if tid not in completed_tasks
                and tid not in running_tasks
                and all(dep in completed_tasks for dep in dag.predecessors(tid))
            ]

            # Start ready tasks
            for task_id in ready_tasks:
                print(f"Starting task: {task_id}")
                running_tasks[task_id] = asyncio.create_task(
                    self.execute_task(project_id, task_map[task_id])
                )

            if not running_tasks:
                if len(completed_tasks) < len(tasks):
                    # This should only happen if there's a bug or unresolvable deps
                    break
                continue

            # Wait for any task to complete
            done, _ = await asyncio.wait(
                running_tasks.values(),
                return_when=asyncio.FIRST_COMPLETED
            )

            for task_future in done:
                # Find which task finished
                finished_task_id = None
                for tid, fut in running_tasks.items():
                    if fut == task_future:
                        finished_task_id = tid
                        break

                if finished_task_id:
                    del running_tasks[finished_task_id]
                    completed_tasks.add(finished_task_id)
                    print(f"Completed task: {finished_task_id}")

    async def execute_task(self, project_id: str, task: Dict[str, Any]):
        """Executes a single task using Coder and Reviewer agents."""
        self.db.update_task_status(task['id'], 'in_progress')

        try:
            # 1. Coder performs the task
            # In a real system, we'd use runner.run_async here
            # For brevity in this demo, we'll simulate the agent interaction
            print(f"Coder working on {task['title']}...")
            await asyncio.sleep(2) # Simulate work

            # 2. Reviewer checks the task
            print(f"Reviewer checking {task['title']}...")
            await asyncio.sleep(1) # Simulate review

            self.db.update_task_status(task['id'], 'completed', result="Success")
        except Exception as e:
            self.db.update_task_status(task['id'], 'failed', error=str(e))
            raise e
