import logging
import uuid
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
    max_steps=25
)

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str


class ResumeRequest(BaseModel):
    id: str


def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread and update the database"""
    try:
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if not db_state:
                return
            
            # Ensure status is running (it should be for newly launched states)
            db_state.status = "running"
            db_state.error = None
            session.commit()
            
            # Convert to Pydantic and run agent (outside session to avoid long transaction)
            working_state = db_to_pydantic(db_state)
        
        # Define progress callback to save state after each step
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
        
        # Run agent with progress callback
        final_state = agent.run(working_state, progress_callback=save_progress)
        
        # Final update to ensure everything is saved
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                db_state.steps = final_state.steps
                db_state.status = final_state.status
                db_state.context = final_state.context
                db_state.pending_tool_calls = final_state.pending_tool_calls
                db_state.error = final_state.error
                db_state.final_answer = final_state.final_answer
                session.commit()
            
    except Exception as e:
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error in background agent execution for {state_id}: {e}")
        traceback.print_exc()
        
        # Mark as failed in database
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                db_state.status = "failed"
                db_state.error = str(e)
                db_state.pending_tool_calls = []
                session.commit()


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


@app.post("/agent/resume", response_model=State)
def agent_resume(payload: ResumeRequest):
    """Resume a paused or interrupted workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        # Prevent concurrent execution
        if db_state.status == "running":
            raise HTTPException(
                status_code=409, 
                detail="Agent is already running for this state"
            )
        
        # Clear error and convert to Pydantic
        db_state.error = None
        session.commit()
        
        working_state = db_to_pydantic(db_state)
    
    # Define progress callback to save state after each step
    def save_progress(state: State):
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
            if db_state:
                db_state.steps = state.steps
                db_state.status = state.status
                db_state.context = state.context
                db_state.pending_tool_calls = state.pending_tool_calls
                db_state.error = state.error
                db_state.final_answer = state.final_answer
                session.commit()
    
    # Run agent (outside session to avoid long transaction)
    try:
        final_state = agent.run(working_state, progress_callback=save_progress)
    except Exception as e:
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error while resuming agent {payload.id}: {e}")
        traceback.print_exc()
        
        # Update failure in database
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
            if db_state:
                db_state.status = "failed"
                db_state.error = str(e)
                db_state.pending_tool_calls = []
                session.commit()
        raise HTTPException(status_code=500, detail=str(e))
    
    # Save final state to database
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if db_state:
            db_state.steps = final_state.steps
            db_state.status = final_state.status
            db_state.context = final_state.context
            db_state.pending_tool_calls = final_state.pending_tool_calls
            db_state.error = final_state.error
            db_state.final_answer = final_state.final_answer
            session.commit()
    
    return final_state
