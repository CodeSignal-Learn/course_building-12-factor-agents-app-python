# Building a 12-Factor Agents App in Python

This project is part of the **"Building a 12-Factor Agents App in Python"** learning path from CodeSignal Learn. It demonstrates how to build reliable, production-ready LLM-powered applications following the 12-Factor Agents methodology.

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
- **`server/`** - FastAPI server exposing REST endpoints for agent operations with SQLite database persistence
- **`client/`** - Example HTTP client demonstrating agent usage

The agent follows a stateless reducer pattern: it takes an input state and event, processes them through controlled steps, and produces an output state. All state is explicitly managed and persisted to a SQLite database, allowing workflows to be resumed, inspected, or debugged at any point. The server provides real-time progress updates as the agent executes.

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

**Note:** The server automatically creates a SQLite database file (`agent_states.db`) in the `src` directory to persist agent states. This enables state recovery, inspection, and resuming interrupted workflows.

### API Endpoints

- **`POST /agent/launch`** - Launch a new agent workflow
  - Request body: `{"input_prompt": "your task description"}`
  - Returns: Initial agent state with unique `id`
  - The agent runs in the background; use the state `id` to poll for progress

- **`GET /agent/state/{state_id}`** - Get the current state of an agent workflow
  - Returns: Complete state including context, status, steps, and results
  - State is updated in real-time as the agent executes, so you can poll this endpoint to see progress

- **`POST /agent/resume`** - Resume a paused or interrupted workflow
  - Request body: `{"id": "state-id"}`
  - Returns: Updated state after resuming execution
  - Returns `409 Conflict` if the agent is already running for this state

## Running the Client

The example client demonstrates how to interact with the agent API:

```bash
cd src
python -m client.main
```

## Project Structure

```
src/
├── core/                    # Core agent implementation
│   ├── agent.py            # Main agent class with progress callbacks
│   ├── client_tool.py      # Tool abstraction
│   ├── models/
│   │   └── state.py        # State model definition (Pydantic)
│   ├── prompts/
│   │   └── base_system.md  # System prompt template
│   └── tools/              # Available tools
│       └── math.py         # Example math tools
├── server/                  # FastAPI server
│   ├── main.py             # API endpoints and background task management
│   └── database.py         # SQLAlchemy models and database session management
├── client/                 # Example client
│   └── main.py             # HTTP client with polling demonstration
└── test.py                 # Local test script for direct agent execution
```

## Key Features

- **Structured Tool Calls**: Natural language requests are converted to schema-validated tool invocations
- **Owned Prompts**: Prompts are version-controlled, file-relative paths work from any directory
- **Context Management**: Strategic context window usage for optimal performance
- **Unified State**: Execution and business state combined in a single source of truth
- **State Persistence**: SQLite database stores all agent states for recovery and inspection
- **Real-Time Progress**: Progress callbacks update the database after each step for live monitoring
- **Controlled Execution**: Explicit control flow with step limits and status tracking
- **Human-in-the-Loop**: Built-in support for requesting human input when needed
- **Stateless Design**: Agent acts as a pure reducer function for easy scaling
- **API-First**: RESTful API allows integration from any interface
- **Concurrency Safety**: Database transactions and status checks prevent race conditions
- **Structured Logging**: Comprehensive logging at INFO level for debugging and monitoring

## Notes

- Always run commands from the `src` directory or set `PYTHONPATH=src` so imports work correctly
- The agent uses a maximum step limit to prevent infinite loops (default: 25 steps, configurable)
- State is automatically persisted to SQLite database (`agent_states.db`) and can be resumed
- Tool calls are validated against schemas before execution
- The agent converts SDK objects to JSON-serializable dicts automatically for database storage
- Background tasks provide non-blocking agent execution with real-time progress updates
- The client example demonstrates polling patterns for monitoring agent progress

## Testing

You can test the agent directly without the server:

```bash
cd src
python test.py
```

This runs the agent locally and demonstrates the core execution flow.

## Learning Path

This project is designed as a hands-on learning experience. As you progress through the CodeSignal Learn path, you'll understand:

- How to structure LLM applications for production use
- The importance of explicit state management and control flow
- Best practices for error handling and recovery
- How to design scalable, maintainable AI systems

For more information about the 12-Factor Agents methodology, visit the [official repository](https://github.com/humanlayer/12-factor-agents).
