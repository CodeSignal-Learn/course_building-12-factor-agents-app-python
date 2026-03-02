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

1. **Initialization**: Takes max_steps (default: 10), model settings. Tool schemas are loaded from JSON files in `core/tools/schemas/`.
2. **Execution Loop** (`run()` method):
   - Process pending_tool_calls from state
   - Built-in tools (`final_answer`, `ask_human`) change status and stop execution
   - Regular tools execute and add results to context
   - After processing pending calls, context is serialized to text using a template and LLM is invoked
   - LLM response adds new tool calls to pending_tool_calls
   - Progress callback fires after each step to persist state
   - Loop continues until status changes or max_steps reached

3. **Tool Execution**: Tools are executed using a match/case statement in `_next_step`:
   - Each tool is a case in the match statement (backend/core/agent.py)
   - Tool functions are defined in `core/tools/functions/`
   - Tool schemas are JSON files in `core/tools/schemas/`
   - Built-in tools (`final_answer`, `ask_human`) have special control flow
   - Regular tools execute, return results, and continue the loop

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
- Use `final_answer` when done
- Use `ask_human` for clarification
- Always prefer tool calls over fabricating results

Tool-only behavior is enforced via `tool_choice="required"` in the OpenAI API call (backend/core/agent.py), not through prompt instructions.

### Context Serialization

The agent serializes the structured context into formatted text before sending it to the LLM:

- **Serialization Function**: `serialize_context_to_text()` in `backend/core/utils/context_serializer.py`
- **Template System**: Uses a markdown template from `backend/core/prompts/context_format.md`
- **Format**:
  ```markdown
  # User Request
  <initial user message>

  # Actions Already Completed (DO NOT REPEAT)

  ✓ COMPLETED: tool_name(arg=val) → Result: {"result": ...}
  ✓ COMPLETED: another_tool(arg=val) → Result: {"result": ...}

  # Next Step
  Decide what tool to call next to make progress on the request.
  ```

This approach provides full control over how the model sees context history and makes it explicit that completed actions should not be repeated.

### File-Relative Prompt Loading

The agent loads prompts using `Path(__file__).resolve().parent` to ensure paths work from any working directory (backend/core/agent.py:26 and backend/core/utils/context_serializer.py:7).

### Resumption Logic

When resuming (state.steps > 0), the agent extends max_steps to allow continuing from where it left off:
```python
max_steps_allowed = (self.max_steps + state.steps) if is_resuming else self.max_steps
```

### Human-in-the-Loop Flow

1. Agent calls `ask_human` tool → status becomes "waiting_human_input"
2. Client detects status during polling
3. Client prompts user (CLI uses `core/tools/functions/human_interaction.py`, UI shows dialog)
4. Client POSTs answer to `/agent/provide_input`
5. Server appends `function_call_output` to context with the answer
6. Agent resumes execution in background task

### Adding New Tools

To add a new tool to the agent, follow these three steps:

1. **Define the function** in `backend/core/tools/functions/` (see `math.py` for examples):
```python
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"
```

2. **Create JSON schema** in `backend/core/tools/schemas/my_tool.json`:
```json
{
  "type": "function",
  "name": "my_tool",
  "description": "Description of what this tool does",
  "parameters": {
    "type": "object",
    "properties": {
      "param": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param"],
    "additionalProperties": false
  }
}
```

3. **Add case to match statement** in `backend/core/agent.py` `_next_step` method:
```python
from core.tools.functions.my_module import my_tool

# In _next_step method, add to the match statement:
case "my_tool":
    try:
        result = my_tool(**call_arguments)
        output = json.dumps({"result": result})
    except Exception as e:
        output = json.dumps({"result": f"Error: {str(e)}"})
```

4. **Load schema in Agent.__init__** in `backend/core/agent.py`:
```python
with open(schemas_dir / "my_tool.json", "r", encoding="utf-8") as f:
    my_tool_schema = json.load(f)

self.tool_schemas = [
    *math_schemas,
    final_answer_schema,
    ask_human_schema,
    my_tool_schema  # Add here
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
