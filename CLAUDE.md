# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 12-Factor Agents application demonstrating production-ready AI agent patterns in Python. The agent follows a stateless reducer architecture: it takes an input state and event, processes them through controlled steps, and produces an output state. All state is explicitly managed and persisted to SQLite.

The project consists of:
- **Backend**: Python FastAPI server with core agent logic (backend/)
- **Frontend**: React UI for agent management (frontend/)

## Development Commands

### Quick Start

Start both backend and frontend:
```bash
./start.sh
```
This starts backend on port 8000 and frontend on port 3000.

### Backend

Run the FastAPI server:
```bash
cd backend
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

Run direct agent test (without server):
```bash
cd backend
python -m tests.test_agent
```

Run HTTP client example:
```bash
cd backend
python -m client.main
```

Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend

Development server:
```bash
cd frontend
npm run dev
```

Build for production:
```bash
cd frontend
npm run build
```

Preview production build:
```bash
cd frontend
npm run preview
```

Install dependencies:
```bash
cd frontend
npm install
```

## Architecture

### Core Agent Pattern

The agent implements a stateless reducer pattern centered around the `State` model (backend/core/models/state.py):
- `id`: Unique identifier
- `steps`: Execution step counter
- `status`: Current status (running, complete, waiting_human_input, max_steps_reached, paused, failed)
- `context`: Full conversation history (messages, tool calls, results)
- `pending_tool_calls`: Queue of tool calls awaiting execution
- `error`: Error message if failed
- `final_answer`: Result when complete

### Agent Execution Flow

The `Agent` class (backend/core/agent.py) implements the core execution loop:

1. **Initialization**: Takes tools, max_steps (default: 10), model settings
2. **Execution Loop** (`run()` method):
   - Process pending_tool_calls from state
   - Built-in tools (`final_answer`, `ask_human`) change status and stop execution
   - Regular tools execute and add results to context
   - After processing pending calls, LLM is invoked with updated context
   - LLM response adds new tool calls to pending_tool_calls
   - Progress callback fires after each step to persist state
   - Loop continues until status changes or max_steps reached

3. **Tool Calling**: Tools are defined via `ClientTool` (backend/core/client_tool.py):
   - Wraps Python functions with automatic schema generation
   - Introspects function signatures to create OpenAI tool schemas
   - Supports optional `require_approval` flag for dangerous operations

4. **Built-in Tools**:
   - `final_answer`: Sets status to "complete" and stores result
   - `ask_human`: Sets status to "waiting_human_input" and pauses execution

### Server Architecture

The FastAPI server (backend/server/main.py) manages agent lifecycle:

- **SQLite Persistence** (backend/server/database.py):
  - States stored in `backend/data/agent_states.db`
  - Database auto-created on first run
  - Uses SQLAlchemy ORM with JSON columns for context/pending_tool_calls

- **Background Execution**:
  - Agents run in FastAPI background tasks
  - Progress callbacks update database after each step
  - Enables real-time polling from clients

- **Concurrency Safety**:
  - Status checks prevent multiple simultaneous runs
  - Database transactions ensure consistency
  - Progress callback checks for external pauses during execution

- **API Endpoints**:
  - `POST /agent/launch`: Create and start new agent
  - `GET /agent/state/{state_id}`: Poll current state
  - `POST /agent/provide_input`: Submit human input and resume
  - `POST /agent/pause`: Pause running agent
  - `POST /agent/resume`: Resume paused/max_steps_reached agent

### Frontend Architecture

React SPA (frontend/src/):
- Uses Vite for fast dev server and builds
- `api/client.js`: HTTP client for backend communication
- `components/`: UI components for task submission, status display, execution view, human input dialog, history sidebar
- Real-time polling updates agent status automatically
- Automatic human-in-the-loop dialog when status is "waiting_human_input"

## Key Implementation Details

### System Prompt

Located at `backend/core/prompts/base_system.md`. The agent is instructed to:
- ONLY call tools (no text output)
- Use `final_answer` when done
- Use `ask_human` for clarification
- Always prefer tool calls over fabricating results

### File-Relative Prompt Loading

The agent loads prompts using `Path(__file__).resolve().parent` to ensure paths work from any working directory (backend/core/agent.py:20).

### Resumption Logic

When resuming (state.steps > 0), the agent extends max_steps to allow continuing from where it left off:
```python
max_steps_allowed = (self.max_steps + state.steps) if is_resuming else self.max_steps
```

### Human-in-the-Loop Flow

1. Agent calls `ask_human` tool → status becomes "waiting_human_input"
2. Client detects status during polling
3. Client prompts user (CLI uses `core/tools/human_interaction.py`, UI shows dialog)
4. Client POSTs answer to `/agent/provide_input`
5. Server appends `function_call_output` to context with the answer
6. Agent resumes execution in background task

### Adding New Tools

1. Define function in `backend/core/tools/` (see `math.py` for examples)
2. Create `ClientTool` instance in `backend/server/main.py`
3. Add to `tools` list passed to Agent constructor

Example:
```python
from core.client_tool import ClientTool

def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"

tools = [
    ClientTool(name="my_tool", description="My tool description", function=my_tool),
    # ... other tools
]
```

## Environment Requirements

- Python 3.10+
- Node.js 16+ and npm
- `OPENAI_API_KEY` environment variable must be set

## Database

SQLite database is automatically created at `backend/data/agent_states.db`. The `backend/data/` directory is gitignored. To reset state, delete this file (it will be recreated on next server start).

## CORS Configuration

The backend allows all origins (`allow_origins=["*"]`) for preview/proxy environments. In production, restrict this to specific frontend domains.

## Logging

Backend uses Python's logging module at INFO level. Logs include timestamps and show agent execution flow, tool calls, and errors. Check console output or redirect to files (start.sh creates backend.log and frontend.log).

## 12-Factor Agents Principles Demonstrated

This codebase demonstrates the 12-Factor Agents methodology:
1. **Structured tool calls**: Natural language → validated tool invocations
2. **Owned prompts**: Version-controlled, file-relative paths
3. **Context management**: Strategic use of context window
4. **Unified state**: Single State model for execution and business logic
5. **Owned control loop**: Explicit `Agent.run()` with step tracking
6. **Stuck detection**: max_steps prevents infinite loops
7. **Small units**: Single-responsibility tools
8. **Error as context**: Errors returned as tool results for learning
9. **Human-in-the-loop**: Built-in `ask_human` tool
10. **Triggerable**: REST API allows launching from any interface
11. **Stateless reducer**: Agent is pure function (state in → state out)
12. **Horizontal scaling**: Stateless design enables multiple agent instances
