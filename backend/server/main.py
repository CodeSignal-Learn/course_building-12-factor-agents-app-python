import json
import logging
import uuid
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

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
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
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
    max_steps=10
)

app = FastAPI()

# Add CORS middleware to allow frontend to communicate with the API
# Allow all origins for preview/proxy environments (can be restricted in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for preview/proxy environments)
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files (built React app)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

logger = logging.getLogger(__name__)
logger.info(f"Serving frontend from {FRONTEND_DIST}")

# Serve static assets (JS, CSS, etc.)
assets_dir = FRONTEND_DIST / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Serve index.html for root and SPA routes
@app.get("/", response_class=HTMLResponse)
async def serve_root():
    return FileResponse(FRONTEND_DIST / "index.html")


class LaunchRequest(BaseModel):
    input_prompt: str


class ResumeRequest(BaseModel):
    id: str


class ProvideInputRequest(BaseModel):
    id: str
    answer: str


def _create_progress_callback(state_id: str):
    """Create a progress callback function that saves state after each step"""
    def save_progress(state: State):
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                db_state.steps = state.steps
                db_state.status = state.status
                db_state.context = state.context
                db_state.pending_tool_calls = state.pending_tool_calls
                db_state.error = state.error
                db_state.final_answer = state.final_answer
                session.commit()
    return save_progress


def _save_state_to_db(state_id: str, state: State):
    """Save a state to the database"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
        if db_state:
            db_state.steps = state.steps
            db_state.status = state.status
            db_state.context = state.context
            db_state.pending_tool_calls = state.pending_tool_calls
            db_state.error = state.error
            db_state.final_answer = state.final_answer
            session.commit()


def _mark_state_failed(state_id: str, error: str):
    """Mark a state as failed in the database"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
        if db_state:
            db_state.status = "failed"
            db_state.error = error
            db_state.pending_tool_calls = []
            session.commit()


def _run_agent_in_background(state_id: str, working_state: Optional[State] = None):
    """Run the agent in a background thread and update the database"""
    try:
        # If working_state not provided, load from database (for launch)
        if working_state is None:
            with get_db_session() as session:
                db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
                if not db_state:
                    return
                
                # Ensure status is running
                db_state.status = "running"
                db_state.error = None
                session.commit()
                
                working_state = db_to_pydantic(db_state)
        else:
            # working_state provided (for resume/provide_input), ensure DB status is running
            with get_db_session() as session:
                db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
                if db_state:
                    db_state.status = "running"
                    db_state.error = None
                    session.commit()
        
        # Run agent with progress callback
        save_progress = _create_progress_callback(state_id)
        final_state = agent.run(working_state, progress_callback=save_progress)
        
        # Final update to ensure everything is saved
        _save_state_to_db(state_id, final_state)
            
    except Exception as e:
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in background agent execution for {state_id}: {e}")
        traceback.print_exc()
        _mark_state_failed(state_id, str(e))


@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
    # Create initial state
    context = [{"role": "user", "content": payload.input_prompt}]
    initial_state = State(id=str(uuid.uuid4()), context=context, status="running")
    
    # Save to database
    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)
        session.commit()
    
    # Run agent in background
    background_tasks.add_task(_run_agent_in_background, initial_state.id)
    
    return initial_state


@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    """Get the current state by ID"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        return db_to_pydantic(db_state)


def _get_call_id_from_state(state: State) -> Optional[str]:
    """Extract the call_id from the last ask_human call in context"""
    for item in reversed(state.context):
        if isinstance(item, dict) and item.get("type") == "function_call" and item.get("name") == "ask_human":
            return item.get("call_id")
    return None


@app.post("/agent/provide_input", response_model=State)
def provide_input(payload: ProvideInputRequest, background_tasks: BackgroundTasks):
    """Provide human input to a state waiting for human input and resume execution"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        # Check status while still in session
        if db_state.status != "waiting_human_input":
            raise HTTPException(
                status_code=400,
                detail=f"State is not waiting for human input. Current status: {db_state.status}"
            )
        
        # Convert to Pydantic while still in session
        working_state = db_to_pydantic(db_state)
    
    # Find the call_id from the last ask_human call
    call_id = _get_call_id_from_state(working_state)
    if not call_id:
        raise HTTPException(
            status_code=400,
            detail="Could not find ask_human call in state context"
        )
    
    # Add the human's answer as a function_call_output to context
    human_response = {
        "type": "function_call_output",
        "call_id": call_id,
        "output": json.dumps({"answer": payload.answer})
    }
    working_state.context.append(human_response)
    
    # Update state in database with new context
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        db_state.context = working_state.context
        db_state.status = "running"  # Change status back to running so agent can continue
        session.commit()
    
    # Run agent in background (non-blocking) - agent was paused, now resume with human input
    background_tasks.add_task(_run_agent_in_background, payload.id, working_state)
    
    # Return updated state immediately
    return working_state


@app.post("/agent/resume", response_model=State)
def agent_resume(payload: ResumeRequest, background_tasks: BackgroundTasks):
    """Resume a paused or interrupted workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        # Prevent concurrent execution
        if db_state.status == "running":
            raise HTTPException(status_code=409, detail="Agent is already running for this state")
        # Prevent resuming while waiting for human input (use provide_input instead)
        if db_state.status == "waiting_human_input":
            raise HTTPException(status_code=400, detail="Agent is waiting for human input")
        
        # Clear error and convert to Pydantic
        db_state.error = None
        session.commit()
        working_state = db_to_pydantic(db_state)
    
    # Run agent in background (non-blocking) - agent was paused, now resume
    background_tasks.add_task(_run_agent_in_background, payload.id, working_state)
    
    # Return current state immediately
    return working_state
