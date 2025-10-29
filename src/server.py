from fastapi import FastAPI
from pydantic import BaseModel

from models.state import State

app = FastAPI()


class LaunchRequest(BaseModel):
    input_prompt: str

class ResumeRequest(BaseModel):
    id: str


@app.post("/agent/lauch", response_model=State)
async def agent_lauch(payload: LaunchRequest):  # keeping route name as requested
    # Create an initial State from the launch input
    initial_state = State(status="initialized", context=[payload.input_prompt])

    final_state = initial_state.status == "complete"

    return final_state


@app.post("/agent/resume", response_model=State)
async def agent_resume(payload: ResumeRequest):
    return State(id=payload.id, status="complete", context=payload.context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


