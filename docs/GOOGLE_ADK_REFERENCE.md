# Google Agent Development Kit (ADK) for Python Documentation

## Introduction

The Google Agent Development Kit (ADK) is an open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control. This document provides a comprehensive overview of the ADK for Python, including its core components, API references, and usage examples.

## Installation

You can install the ADK for Python using uv.

**Stable Release:**

```bash
uv add google-adk
```

**Development Version:**

```bash
uv add git+https://github.com/google/adk-python.git@main
```

## Core Components

The ADK for Python is comprised of several key components that work together to enable the creation and management of AI agents.

### Agents

Agents are the fundamental building blocks of the ADK. They are responsible for processing input, interacting with models and tools, and generating responses.

**`Agent` Class**

The `Agent` class is the primary class for creating agents. It can be configured with a name, a model, an instruction, a description, and a list of tools.

**`LlmAgent` and `BaseAgent`**

The `LlmAgent` is a powerful and flexible agent that leverages large language models (LLMs) to perform a wide range of tasks. It can be configured with instructions, tools, and examples to customize its behavior. The `BaseAgent` class is the base class for all agents in the ADK.

### Models

The ADK for Python supports various language models, including Gemini and models from other providers through LiteLLM.

**`LiteLlm` Class**

The `LiteLlm` class allows you to use models from providers like Ollama.

### Tools

Tools are used to extend the capabilities of agents, allowing them to interact with external systems and perform a wider range of tasks. The ADK provides a variety of pre-built tools, such as `google_search` and tools for interacting with BigQuery. You can also create your own custom tools.

## Advanced Features

### Session State Management

The ADK provides a mechanism for managing session state, allowing agents to maintain context across multiple interactions with a user.

### Human-in-the-Loop

The ADK supports human-in-the-loop workflows, where a human can review and approve the actions of an agent before they are executed.

### Agent-to-Agent Communication

The ADK enables agent-to-agent (A2A) communication, allowing you to build complex, multi-agent systems where agents can collaborate to accomplish tasks.

## API Reference

This section provides a detailed reference for the most important classes and methods in the ADK for Python.

### `Agent`

**Constructor:**

```python
Agent(
    name: str,
    model: str,
    instruction: str,
    description: str,
    tools: list
)
```

### `LiteLlm`

**Constructor:**

```python
LiteLlm(model: str)
```

## Usage Examples

This section provides examples of how to use the ADK for Python to build and deploy AI agents.

### Defining a Single Agent

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.0-flash", # Or your preferred Gemini model
    instruction="You are a helpful assistant. Answer user questions using Google Search when needed.",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

### Defining a Multi-Agent System

```python
from google.adk.agents import LlmAgent, BaseAgent

# Define individual agents
greeter = LlmAgent(name="greeter", model="gemini-2.0-flash", ...)
task_executor = LlmAgent(name="task_executor", model="gemini-2.0-flash", ...)

# Create parent agent and assign children via sub_agents
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    description="I coordinate greetings and tasks.",
    sub_agents=[ # Assign sub_agents here
        greeter,
        task_executor
    ]
)
```

### Using an Ollama Model

```python
from google.adk.agents import Agent
from google.adk.models import LiteLlm

root_agent = Agent(
    model=LiteLlm(model="ollama_chat/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

### Evaluating an Agent

```bash
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

## Deployment

You can deploy your ADK agents as a web service using `adk web` or as an API server using `adk api_server`.

**`adk web`**

The `adk web` command starts a local web server that you can use to interact with your agents.

```bash
adk web
```

**`adk api_server`**

The `adk api_server` command starts a FastAPI server that exposes your agents as API endpoints.

```bash
adk api_server
```

## Contributing

The ADK is an open-source project, and contributions are welcome. Please see the [CONTRIBUTING.md](https://github.com/google/adk-python/blob/main/CONTRIBUTING.md) file for more information.
