import os
import shutil
import subprocess
from typing import Optional
import json

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/tmp/adk-workspaces")

def clone_repository(repo_url: str, project_id: str) -> str:
    """Clones a repository into a project-specific workspace.

    Args:
        repo_url: The URL of the repository to clone (https or git)
        project_id: A unique identifier for the project

    Returns:
        str: JSON string with status and local path
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)

    if os.path.exists(workspace_path):
        # If it exists, we might want to refresh it or just return it
        # For now, let's assume we want a fresh clone if requested
        shutil.rmtree(workspace_path)

    os.makedirs(WORKSPACE_ROOT, exist_ok=True)

    try:
        subprocess.run(
            ["git", "clone", repo_url, workspace_path],
            check=True,
            capture_output=True,
            text=True
        )
        return json.dumps({
            "status": "success",
            "path": workspace_path,
            "message": f"Repository cloned to {workspace_path}"
        })
    except subprocess.CalledProcessError as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to clone repository: {e.stderr}"
        })

def list_files_in_workspace(project_id: str, path: str = ".") -> str:
    """Lists files in the project workspace.

    Args:
        project_id: The project identifier
        path: Relative path within the workspace

    Returns:
        str: JSON string with file list
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)
    target_path = os.path.join(workspace_path, path)

    if not os.path.exists(target_path):
        return json.dumps({"error": f"Path {path} does not exist in workspace"})

    files = os.listdir(target_path)
    return json.dumps({"files": files})

def read_file_in_workspace(project_id: str, file_path: str) -> str:
    """Reads a file from the project workspace.

    Args:
        project_id: The project identifier
        file_path: Relative path to the file

    Returns:
        str: Content of the file or error
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)
    full_path = os.path.join(workspace_path, file_path)

    if not os.path.exists(full_path):
        return json.dumps({"error": f"File {file_path} not found"})

    try:
        with open(full_path, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        return json.dumps({"error": str(e)})

def write_file_in_workspace(project_id: str, file_path: str, content: str) -> str:
    """Writes content to a file in the project workspace.

    Args:
        project_id: The project identifier
        file_path: Relative path to the file
        content: Content to write

    Returns:
        str: Success or error message
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)
    full_path = os.path.join(workspace_path, file_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    try:
        with open(full_path, "w") as f:
            f.write(content)
        return json.dumps({"status": "success", "message": f"File {file_path} written"})
    except Exception as e:
        return json.dumps({"error": str(e)})
