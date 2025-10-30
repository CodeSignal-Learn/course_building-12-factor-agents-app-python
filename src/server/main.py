import threading
import uuid
from typing import Set

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from core.models.state import State
from core.agent import Agent
from core.client_tool import ClientTool
from core.tools.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root,
)

# Create a list of ClientTools with the given functions
tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

# Create an Agent with the tools
agent = Agent(
    tools=tools,
    max_steps=25
)

app = FastAPI()

# In-memory database to store states by ID
state_database: dict[str, State] = {}
state_lock = threading.Lock()
# Track which states are currently being executed to prevent concurrent runs
running_states: Set[str] = set()


def _begin_run(state_id: str) -> bool:
    """Mark a state as running if not already running. Returns True if acquired."""
    with state_lock:
        if state_id in running_states:
            return False
        running_states.add(state_id)
        return True


def _end_run(state_id: str):
    """Clear the running mark for a state id."""
    with state_lock:
        running_states.discard(state_id)


class LaunchRequest(BaseModel):
    input_prompt: str


class ResumeRequest(BaseModel):
    id: str


def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread and update the state database safely."""
    if not _begin_run(state_id):
        # Another execution is already in progress for this state
        return

    try:
        with state_lock:
            original = state_database.get(state_id)
            if not original:
                _end_run(state_id)
                return
            # Clear previous error and work on a deep copy
            original.error = None
            working = original.model_copy(deep=True)

        # Run the agent with the deep copy of the state
        final_state = agent.run(working)

        # Atomically swap the stored state with the updated copy
        with state_lock:
            if state_id in state_database:
                state_database[state_id] = final_state
    except Exception as e:
        import traceback
        print(f"Error in background agent execution: {e}")
        traceback.print_exc()
        with state_lock:
            if state_id in state_database:
                state_database[state_id].status = "failed"
                state_database[state_id].error = str(e)
                state_database[state_id].pending_tool_calls = []
    finally:
        _end_run(state_id)


@app.post("/agent/launch", response_model=State)
async def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    # Create initial state with status "running"
    context = [
        {"role": "user", "content": payload.input_prompt},
    ]
    initial_state = State(id=str(uuid.uuid4()), context=context, status="running")
    
    # Store state in database
    with state_lock:
        state_database[initial_state.id] = initial_state
    
    # Run agent in background with the state
    background_tasks.add_task(_run_agent_in_background, initial_state.id)
    
    # Return immediately
    return initial_state


@app.get("/agent/state/{state_id}", response_model=State)
async def get_state(state_id: str):
    """Get the current state by ID"""
    with state_lock:
        state = state_database.get(state_id)
        if not state:
            raise HTTPException(status_code=404, detail="State not found")
        # Return a deep-copy snapshot to avoid exposing in-progress mutations
        return state.model_copy(deep=True)


@app.post("/agent/resume", response_model=State)
async def agent_resume(payload: ResumeRequest):
    # Retrieve and prepare state safely
    with state_lock:
        original = state_database.get(payload.id)
        if original:
            original.error = None
        if not original:
            raise HTTPException(status_code=404, detail="State not found")
        # Prevent concurrent execution for the same state
        if payload.id in running_states:
            raise HTTPException(status_code=409, detail="Agent is already running for this state")
        # Mark as running and work on a deep copy
        running_states.add(payload.id)
        working = original.model_copy(deep=True)

    try:
        final_state = agent.run(working)
        with state_lock:
            state_database[payload.id] = final_state
    except Exception as e:
        import traceback
        print(f"Error while resuming agent {payload.id}: {e}")
        traceback.print_exc()
        with state_lock:
            # Mark failure on the stored state
            original.status = "failed"
            original.error = str(e)
            original.pending_tool_calls = []
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        _end_run(payload.id)

    return final_state