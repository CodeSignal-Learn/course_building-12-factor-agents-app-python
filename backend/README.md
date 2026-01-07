# 12-Factor Agents Backend

Python backend implementing a production-ready AI agent system following the 12-Factor Agents methodology.

## Quick Start

Install dependencies:
```bash
pip install -r requirements.txt
```

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Start the server:
```bash
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

## Architecture

The backend implements a stateless reducer pattern where agents take input state and produce output state. All execution state is persisted to SQLite.

### Directory Structure

```
backend/
├── core/                    # Core agent implementation
│   ├── agent.py            # Main Agent class with match/case tool execution
│   ├── models/
│   │   └── state.py        # Pydantic State model
│   ├── prompts/
│   │   ├── base_system.md  # System prompt
│   │   └── context_format.md # Context serialization template
│   ├── tools/
│   │   ├── functions/      # Tool implementations (Python functions)
│   │   │   ├── math.py
│   │   │   └── human_interaction.py
│   │   └── schemas/        # Tool schemas (JSON)
│   │       ├── math.json
│   │       ├── final_answer.json
│   │       └── ask_human.json
│   └── utils/
│       └── context_serializer.py # Context-to-text formatter
├── server/                  # FastAPI server
│   ├── main.py             # API endpoints
│   └── database.py         # SQLAlchemy models
├── client/
│   └── main.py             # Example HTTP client
├── tests/
│   └── test_agent.py       # Local agent test
└── data/
    └── agent_states.db     # SQLite database (auto-created)
```

## Running the Server

Start the FastAPI server:
```bash
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

The server:
- Creates SQLite database at `data/agent_states.db` on first run
- Runs agents in background tasks
- Updates state after each step via progress callbacks
- Enables real-time polling from clients

## API Endpoints

### Launch Agent
```bash
POST /agent/launch
Content-Type: application/json

{
  "input_prompt": "Calculate the square root of 16"
}
```

Returns initial state with unique `id`. Agent runs in background.

### Get State
```bash
GET /agent/state/{state_id}
```

Returns current state including context, status, steps, and results. Poll this endpoint to monitor progress.

### Provide Human Input
```bash
POST /agent/provide_input
Content-Type: application/json

{
  "id": "state-id",
  "answer": "Your response here"
}
```

Used when agent status is `"waiting_human_input"`. Automatically resumes execution.

### Resume Agent
```bash
POST /agent/resume
Content-Type: application/json

{
  "id": "state-id"
}
```

Resumes a paused or `max_steps_reached` agent.

### Pause Agent
```bash
POST /agent/pause
Content-Type: application/json

{
  "id": "state-id"
}
```

Pauses a running agent.

## Running the Example Client

The client demonstrates polling and human-in-the-loop workflow:

```bash
python -m client.main
```

The client:
- Launches an agent
- Polls for status updates
- Detects `waiting_human_input` status
- Prompts user for input via CLI
- Submits answer and continues

## Running Tests

Test the agent directly without the server:

```bash
python -m tests.test_agent
```

This runs a local agent instance to verify core functionality.

## Adding New Tools

Follow these steps to add a tool:

### 1. Define the Function

Create the function in `core/tools/functions/`:

```python
# core/tools/functions/my_tools.py
def my_tool(param: str) -> str:
    """Tool description"""
    # Your implementation
    return f"Result: {param}"
```

### 2. Create JSON Schema

Create schema file in `core/tools/schemas/my_tool.json`:

```json
{
  "type": "function",
  "name": "my_tool",
  "description": "What this tool does",
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

### 3. Add to Agent Match Statement

In `core/agent.py`, import and add case:

```python
from core.tools.functions.my_tools import my_tool

# In _next_step method, add to match statement:
case "my_tool":
    try:
        result = my_tool(**call_arguments)
        output = json.dumps({"result": result})
    except Exception as e:
        output = json.dumps({"result": f"Error: {str(e)}"})
```

### 4. Load Schema in Agent.__init__

In `core/agent.py` `__init__` method:

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

## Agent Execution Flow

1. **Initialize Agent**: Load schemas from JSON files
2. **Process Pending Tool Calls**:
   - Built-in tools (`ask_human`, `final_answer`) change status and return
   - Regular tools execute and add results to context
3. **Serialize Context**: Convert structured context to formatted text using template
4. **Call LLM**: Send serialized context with `tool_choice="required"`
5. **Parse Response**: Extract tool calls and add to `pending_tool_calls`
6. **Repeat**: Loop continues until status changes or max_steps reached

## Context Serialization

The agent serializes context into this format before sending to LLM:

```markdown
# User Request
<user's prompt>

# Actions Already Completed (DO NOT REPEAT)

✓ COMPLETED: tool_name(arg=val) → Result: {"result": ...}
✓ COMPLETED: another_tool(arg=val) → Result: {"result": ...}

# Next Step
Decide what tool to call next to make progress on the request.
```

This format is defined in `core/prompts/context_format.md` and applied by `core/utils/context_serializer.py`.

## Database

SQLite database stores all agent states with these fields:
- `id`: Unique state identifier
- `steps`: Step counter
- `status`: Current status (running, complete, waiting_human_input, etc.)
- `context`: Full conversation history (JSON)
- `pending_tool_calls`: Queued tool calls (JSON)
- `error`: Error message if failed
- `final_answer`: Result when complete

To reset the database, delete `data/agent_states.db` (will be recreated on next start).

## System Prompt

Located at `core/prompts/base_system.md`. Instructs the agent to:
- Use `final_answer` when done
- Use `ask_human` for clarification
- Prefer tool calls over fabricating results

Tool-only behavior is enforced via `tool_choice="required"` in the API call, not through prompts.

## Logging

The backend uses Python's logging module at INFO level. Logs include:
- Agent execution flow
- Tool calls and results
- Step progress
- Errors and exceptions

Check console output or redirect to files.

## 12-Factor Agents Principles

This backend demonstrates:

1. **Structured tool calls**: Natural language → validated tool invocations
2. **Owned prompts**: Version-controlled, file-relative paths
3. **Context management**: Serialization with explicit format control
4. **Unified state**: Single State model for all data
5. **Owned control loop**: Explicit `Agent.run()` with step tracking
6. **Stuck detection**: `max_steps` prevents infinite loops
7. **Small units**: Single-responsibility tools
8. **Error as context**: Errors returned as tool results
9. **Human-in-the-loop**: Built-in `ask_human` tool
10. **Triggerable**: REST API from any interface
11. **Stateless reducer**: Agent is pure function (state in → state out)
12. **Horizontal scaling**: Stateless design enables multiple instances

## Requirements

- Python 3.10+ (requires match/case statements)
- OpenAI API key
- Dependencies in `requirements.txt`
