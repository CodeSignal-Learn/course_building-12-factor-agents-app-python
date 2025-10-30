from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import threading
import uuid

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


class LaunchRequest(BaseModel):
    input_prompt: str


class ResumeRequest(BaseModel):
    id: str


def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread and update the state database"""
    with state_lock:
        state = state_database.get(state_id)
        if state:
            state.error = None

    if not state:
        return

    try:
        # Run the agent using the same state object stored in the database
        agent.run(state)
    except Exception as e:
        # Log the error and update state with error status
        import traceback
        print(f"Error in background agent execution: {e}")
        traceback.print_exc()
        with state_lock:
            if state_id in state_database:
                state_database[state_id].status = "failed"
                state_database[state_id].error = str(e)
                state_database[state_id].pending_tool_calls = []


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
        return state


@app.post("/agent/resume", response_model=State)
async def agent_resume(payload: ResumeRequest):
    # Retrieve state from database
    with state_lock:
        state = state_database.get(payload.id)
        if state:
            state.error = None
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    try:
        # Run agent with the stored state (updates happen in place)
        final_state = agent.run(state)
    except Exception as e:
        import traceback
        print(f"Error while resuming agent {payload.id}: {e}")
        traceback.print_exc()
        with state_lock:
            state.status = "failed"
            state.error = str(e)
            state.pending_tool_calls = []
        raise HTTPException(status_code=500, detail=str(e))

    return final_state