import docker
import os
import json

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/tmp/adk-workspaces")

def execute_command_in_container(project_id: str, command: str, image: str = "python:3.12-slim") -> str:
    """Executes a command inside a Docker container for isolated code execution.

    Args:
        project_id: Project identifier
        command: Command to run (e.g., 'pytest' or 'python app.py')
        image: Docker image to use for execution

    Returns:
        str: Result of the execution (stdout and stderr)
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)

    if not os.path.exists(workspace_path):
        return json.dumps({"error": f"Project workspace {project_id} not found"})

    client = docker.from_env()

    try:
        container = client.containers.run(
            image=image,
            command=command,
            volumes={
                workspace_path: {"bind": "/workspace", "mode": "rw"}
            },
            working_dir="/workspace",
            detach=True
        )

        result = container.wait()
        logs = container.logs().decode("utf-8")
        container.remove()

        return json.dumps({
            "status": "success",
            "exit_code": result["StatusCode"],
            "output": logs
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_tests_in_container(project_id: str, test_command: str = "pytest", image: str = "python:3.12-slim") -> str:
    """Specialized tool for running tests in a container.

    Args:
        project_id: Project identifier
        test_command: Command to run tests
        image: Docker image to use

    Returns:
        str: JSON with test results
    """
    return execute_command_in_container(project_id, test_command, image)
