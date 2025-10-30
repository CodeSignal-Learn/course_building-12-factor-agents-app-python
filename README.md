# Building a 12-Factor Agents App

This project is part of the **"Building a 12-Factor Agents App"** learning path from CodeSignal Learn. It demonstrates how to build reliable, production-ready LLM-powered applications following the 12-Factor Agents methodology.

## What are 12-Factor Agents?

The **12-Factor Agents** framework, introduced by AI engineer Dex Horthy, provides a blueprint for building reliable, scalable, and maintainable applications powered by Large Language Models (LLMs). Inspired by Heroku's classic 12-Factor App methodology, this framework brings proven software engineering discipline to the world of AI agents.

### Core Principles

The framework organizes twelve key principles into four main categories:

1. **Structure Prompts, Tools, and Context** - Converting natural language to structured tool calls, owning your prompts, managing context windows strategically, and treating tools as structured outputs.

2. **Manage State and Control Flow** - Unifying execution and business state, owning the control loop, detecting when agents get stuck, and breaking down complex tasks into small, focused units.

3. **Error Handling and Human Interaction** - Treating errors as context for learning, and designing effective human-in-the-loop workflows.

4. **Scalability and Architecture** - Making agents triggerable from anywhere, and designing them as stateless reducers for horizontal scaling.

The key insight: successful production AI applications aren't fully autonomous agents—they're well-engineered traditional software with LLM capabilities strategically integrated at key points. As the community says: *"LLMs provide intelligence. The 12 Factors provide reliability."*

## Project Overview

This project implements a production-ready AI agent system that demonstrates the 12-Factor Agents principles in practice. The agent can:

- **Process natural language requests** and convert them into structured tool calls
- **Execute complex multi-step workflows** with deterministic control flow
- **Maintain unified state** across execution steps
- **Handle errors gracefully** and learn from them
- **Support human-in-the-loop** interactions when needed
- **Resume interrupted workflows** from saved state
- **Scale horizontally** through stateless design

### Architecture

The project is organized into three main components:

- **`core/`** - Core agent logic, state management, and tool definitions
- **`server/`** - FastAPI server exposing REST endpoints for agent operations
- **`client/`** - Example HTTP client demonstrating agent usage

The agent follows a stateless reducer pattern: it takes an input state and event, processes them through controlled steps, and produces an output state. All state is explicitly managed and can be persisted, resumed, or inspected at any point.

## Requirements

- Python 3.10+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Running the Server

Start the FastAPI server from the `src` directory:

```bash
cd src
python -m uvicorn server.main:app --host 0.0.0.0 --port 3000 --reload
```

The API will be available at `http://localhost:3000`.

### API Endpoints

- **`POST /agent/launch`** - Launch a new agent workflow
  - Request body: `{"input_prompt": "your task description"}`
  - Returns: Initial agent state with unique `id`

- **`GET /agent/state/{state_id}`** - Get the current state of an agent workflow
  - Returns: Complete state including context, status, and results

- **`POST /agent/resume`** - Resume a paused or interrupted workflow
  - Request body: `{"id": "state-id"}`
  - Returns: Updated state after resuming execution

## Running the Client

The example client demonstrates how to interact with the agent API:

```bash
cd src
python -m client.main
```

Alternatively, from the repository root:

```bash
PYTHONPATH=src python src/client/main.py
```

## Project Structure

```
src/
├── core/                    # Core agent implementation
│   ├── agent.py            # Main agent class
│   ├── client_tool.py      # Tool abstraction
│   ├── models/
│   │   └── state.py        # State model definition
│   ├── prompts/
│   │   └── base_system.md  # System prompt template
│   └── tools/              # Available tools
│       └── math.py         # Example math tools
├── server/                  # FastAPI server
│   └── main.py             # API endpoints and state management
└── client/                 # Example client
    └── main.py             # HTTP client demonstration
```

## Key Features

- **Structured Tool Calls**: Natural language requests are converted to schema-validated tool invocations
- **Owned Prompts**: Prompts are version-controlled and easily editable
- **Context Management**: Strategic context window usage for optimal performance
- **Unified State**: Execution and business state combined in a single source of truth
- **Controlled Execution**: Explicit control flow with step limits and status tracking
- **Human-in-the-Loop**: Built-in support for requesting human input when needed
- **Stateless Design**: Agent acts as a pure reducer function for easy scaling
- **API-First**: RESTful API allows integration from any interface

## Notes

- Always run commands from the `src` directory or set `PYTHONPATH=src` so imports work correctly
- The agent uses a maximum step limit to prevent infinite loops
- State can be persisted and resumed, enabling long-running workflows
- Tool calls are validated against schemas before execution

## Learning Path

This project is designed as a hands-on learning experience. As you progress through the CodeSignal Learn path, you'll understand:

- How to structure LLM applications for production use
- The importance of explicit state management and control flow
- Best practices for error handling and recovery
- How to design scalable, maintainable AI systems

For more information about the 12-Factor Agents methodology, visit the [official repository](https://github.com/humanlayer/12-factor-agents).
