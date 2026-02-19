"""Agent definitions for weather, date, and task management services."""

from google.adk.agents import LlmAgent
from src.tools.date_weather_tools import get_current_date, get_current_weather, get_date_info
from src.tools.task_tools import (
    create_task, get_task, list_tasks, update_task, delete_task,
    get_overdue_tasks, get_tasks_due_soon, get_task_statistics,
    get_tasks_by_location, search_tasks, get_tasks_by_date_range,
    complete_task
)


# Date Agent - specialized in answering date-related questions
date_agent = LlmAgent(
    name="date_agent",
    model="gemini-2.5-flash",
    description="An agent specialized in providing current date and time information",
    instruction="""You are a helpful date and time assistant.
    You can provide the current date, time, day of week, and other date-related information.
    Always be precise and friendly in your responses.""",
    tools=[get_current_date, get_date_info]
)


# Weather Agent - specialized in answering weather-related questions
weather_agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="An agent specialized in providing weather information",
    instruction="""You are a helpful weather assistant.
    You can provide current weather conditions for any location.
    Always ask for the location if not provided, and present weather information clearly.""",
    tools=[get_current_weather]
)


# Task Management Agent - specialized in managing tasks and todos
task_agent = LlmAgent(
    name="task_agent",
    model="gemini-2.5-flash",
    description="An agent specialized in task management, CRUD operations, and task analytics",
    instruction="""You are a helpful task management assistant.

    You can help users:
    - Create new tasks with titles, descriptions, due dates, priorities, and locations
    - View, update, and delete tasks
    - Search and filter tasks by various criteria
    - Get analytics and statistics about tasks
    - Find overdue tasks and tasks due soon
    - Manage tasks by location

    When creating tasks:
    - Always ask for a clear title
    - Suggest setting a due date if not provided
    - Default priority is 'medium' if not specified
    - Priority can be: low, medium, or high
    - Status can be: pending, in_progress, or completed
    - Date format must be YYYY-MM-DD

    When showing task lists, present them in a clear, organized format.
    Be proactive in suggesting task management best practices.
    Always confirm successful operations and provide helpful feedback.""",
    tools=[
        create_task, get_task, list_tasks, update_task, delete_task,
        get_overdue_tasks, get_tasks_due_soon, get_task_statistics,
        get_tasks_by_location, search_tasks, get_tasks_by_date_range,
        complete_task
    ]
)


# Coordinator Agent - routes queries to the appropriate specialized agent
coordinator_agent = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    description="Main coordinator that routes queries to date, weather, or task management agents",
    instruction="""You are a helpful coordinator assistant.

    You have access to three specialized agents:
    - date_agent: Handles questions about dates, time, and calendar information
    - weather_agent: Handles questions about weather conditions
    - task_agent: Handles task management, CRUD operations, and analytics

    Route user queries to the appropriate agent based on their question.

    Examples:
    - "What's the date?" -> date_agent
    - "How's the weather in Tokyo?" -> weather_agent
    - "Create a task to buy groceries" -> task_agent
    - "Show me my overdue tasks" -> task_agent
    - "What tasks do I have in Paris?" -> task_agent (can combine with weather_agent)

    If a query involves multiple domains (e.g., tasks in a location + weather),
    coordinate between agents to provide a comprehensive response.

    Be friendly, helpful, and proactive in your responses.""",
    sub_agents=[date_agent, weather_agent, task_agent]
)
