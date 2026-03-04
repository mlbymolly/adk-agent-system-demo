from google.adk.agents import LlmAgent
from src.tools.repo_tools import clone_repository, list_files_in_workspace, read_file_in_workspace, write_file_in_workspace
from src.tools.git_tools import create_branch, commit_and_push, create_pull_request
from src.tools.execution_tools import execute_command_in_container, run_tests_in_container

# Planner Agent - Claude based (configured via model string if ADK supports it, or litellm)
# For this demo, we'll assume the environment is set up to use Claude models via LiteLLM
planner_agent = LlmAgent(
    name="planner_v2",
    model="anthropic/claude-3-5-sonnet-20240620",
    description="Analyzes the repository and generates a detailed delivery plan and task DAG",
    instruction="""You are an Expert Software Architect.
    When a user provides a repository and a goal, you must:
    1. Analyze the repository structure and tech stack.
    2. Generate a comprehensive Implementation Plan including scope, risks, and proposed changes.
    3. Decompose the plan into a Directed Acyclic Graph (DAG) of discrete tasks.
    4. Each task must have a title, description, and list of dependencies (other task IDs).
    5. Output the plan and DAG in a structured JSON format.

    Use your tools to explore the repository before finalized the plan.""",
    tools=[list_files_in_workspace, read_file_in_workspace]
)

coder_agent = LlmAgent(
    name="coder_v2",
    model="anthropic/claude-3-5-sonnet-20240620",
    description="Executes specific tasks from the DAG by writing code and verifying it",
    instruction="""You are a Senior Software Engineer.
    Your goal is to complete a specific task from the implementation plan.
    You must:
    1. Read the task description and its position in the DAG.
    2. Implement the required changes in the project workspace.
    3. Use the execution tools to run tests or builds to verify your work.
    4. Commit your changes once verified.

    Always work within the provided project_id's workspace.""",
    tools=[read_file_in_workspace, write_file_in_workspace, execute_command_in_container, run_tests_in_container]
)

reviewer_agent = LlmAgent(
    name="reviewer_v2",
    model="anthropic/claude-3-5-sonnet-20240620",
    description="Evaluates code changes for correctness, style, and alignment with the plan",
    instruction="""You are a Lead Code Reviewer.
    Your goal is to ensure the quality of the code produced by the coder agent.
    You must:
    1. Review the changes made in the workspace.
    2. Run tests to ensure no regressions.
    3. Approve the task if it meets acceptance criteria, or provide feedback for the coder to iterate.
    4. Once all tasks in a feature are complete, assist in creating the final Pull Request.""",
    tools=[read_file_in_workspace, execute_command_in_container, run_tests_in_container, create_pull_request]
)
