from fastapi import FastAPI
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


class LaunchRequest(BaseModel):
    input_prompt: str


class ResumeRequest(BaseModel):
    id: str


@app.post("/agent/launch", response_model=State)
async def agent_launch(payload: LaunchRequest):
    final_state = agent.run(payload.input_prompt)
    return final_state


@app.post("/agent/resume", response_model=State)
async def agent_resume(payload: State):
    final_state = agent.resume(payload)
    return final_state