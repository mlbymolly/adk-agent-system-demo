import subprocess
import os
import json

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/tmp/adk-workspaces")

def create_branch(project_id: str, branch_name: str) -> str:
    """Creates a new branch in the project workspace.

    Args:
        project_id: The project identifier
        branch_name: Name of the new branch

    Returns:
        str: Success or error message
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)

    try:
        subprocess.run(
            ["git", "-C", workspace_path, "checkout", "-b", branch_name],
            check=True,
            capture_output=True,
            text=True
        )
        return json.dumps({"status": "success", "message": f"Branch {branch_name} created"})
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Failed to create branch: {e.stderr}"})

def commit_and_push(project_id: str, message: str, branch_name: str) -> str:
    """Stages all changes, commits, and pushes to remote.

    Args:
        project_id: The project identifier
        message: Commit message
        branch_name: Branch to push

    Returns:
        str: Success or error message
    """
    workspace_path = os.path.join(WORKSPACE_ROOT, project_id)

    try:
        subprocess.run(["git", "-C", workspace_path, "add", "."], check=True)
        subprocess.run(["git", "-C", workspace_path, "commit", "-m", message], check=True)
        # Assuming remote name is "origin"
        subprocess.run(["git", "-C", workspace_path, "push", "origin", branch_name], check=True)
        return json.dumps({"status": "success", "message": "Changes pushed"})
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Failed to push changes: {e.stderr}"})

def create_pull_request(project_id: str, title: str, body: str, head_branch: str, base_branch: str = "main") -> str:
    """MOCK tool for creating a Pull Request.

    Args:
        project_id: Project identifier
        title: PR title
        body: PR description
        head_branch: Feature branch
        base_branch: Target branch

    Returns:
        str: JSON with PR link (mock)
    """
    # In a real scenario, this would call GitHub/GitLab API using the environment variables
    # For now, let's just return a mock success
    return json.dumps({
        "status": "success",
        "message": "Pull request created successfully (MOCK)",
        "pr_url": f"https://github.com/mock/repo/pull/123",
        "title": title
    })
