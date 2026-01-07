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

The project is organized into four main components:

- **`backend/core/`** - Core agent logic, state management, and tool definitions
- **`backend/server/`** - FastAPI server exposing REST endpoints for agent operations with SQLite database persistence
- **`backend/client/`** - Example HTTP client demonstrating agent usage
- **`frontend/`** - React web UI for managing and monitoring agents

The agent follows a stateless reducer pattern: it takes an input state and event, processes them through controlled steps, and produces an output state. All state is explicitly managed and persisted to a SQLite database, allowing workflows to be resumed, inspected, or debugged at any point. The server provides real-time progress updates as the agent executes.

## Requirements

- Python 3.10+
- Node.js 16+ and npm
- OpenAI API key

## Quick Start

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Install dependencies:
```bash
# Backend
cd backend && pip install -r requirements.txt && cd ..

# Frontend
cd frontend && npm install && cd ..
```

3. Start both servers:
```bash
./start.sh
```

This launches:
- **Backend API** on `http://localhost:8000`
- **Frontend UI** on `http://localhost:3000`

Press `Ctrl+C` to stop both servers.

## Project Components

### Backend
Python FastAPI server implementing the core agent system.

- **API endpoints** for launching, monitoring, and controlling agents
- **SQLite persistence** for agent states
- **Background execution** with real-time progress updates
- **Human-in-the-loop** support via `ask_human` tool

See [backend/README.md](backend/README.md) for detailed documentation, API reference, and how to add new tools.

### Frontend
React web interface for agent management.

- **Launch agents** with natural language prompts
- **Real-time monitoring** of agent execution
- **Execution history** sidebar
- **Interactive human-in-the-loop** dialogs
- **Resume/pause controls**

See [frontend/README.md](frontend/README.md) for frontend-specific documentation.

## Project Structure

```
backend/           # Python FastAPI server
├── core/         # Agent implementation (Agent, State, tools, prompts)
├── server/       # API endpoints and database
├── client/       # Example HTTP client
└── tests/        # Test scripts

frontend/         # React web UI
└── src/          # Components, API client, app logic
```

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for detailed structure.

## 12-Factor Agents Principles

This project demonstrates all 12 factors:

1. **Structured tool calls** - Natural language → validated tool invocations
2. **Owned prompts** - Version-controlled, file-relative paths
3. **Context management** - Serialized context with explicit format control
4. **Unified state** - Single State model for all data
5. **Owned control loop** - Explicit `Agent.run()` with step tracking
6. **Stuck detection** - `max_steps` prevents infinite loops
7. **Small units** - Single-responsibility tools
8. **Error as context** - Errors returned as tool results
9. **Human-in-the-loop** - Built-in `ask_human` tool
10. **Triggerable** - REST API from any interface
11. **Stateless reducer** - Agent is pure function (state in → state out)
12. **Horizontal scaling** - Stateless design enables multiple instances

See [backend/README.md](backend/README.md) for implementation details.

## Learning Path

This project is designed as a hands-on learning experience. As you progress through the CodeSignal Learn path, you'll understand:

- How to structure LLM applications for production use
- The importance of explicit state management and control flow
- Best practices for error handling and recovery
- How to design scalable, maintainable AI systems

For more information about the 12-Factor Agents methodology, visit the [official repository](https://github.com/humanlayer/12-factor-agents).
