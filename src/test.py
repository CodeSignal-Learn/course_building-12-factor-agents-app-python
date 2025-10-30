import os
import json
import uuid
from pathlib import Path

from core.agent import Agent
from core.client_tool import ClientTool
from core.models.state import State
from core.tools.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root,
)


# Ensure working directory is the src/ folder so relative prompt paths resolve
os.chdir(Path(__file__).resolve().parent)


def build_agent() -> Agent:
    tools = [
        ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
        ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
        ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
        ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
        ClientTool(name="power", description="Raise a number to a power", function=power),
        ClientTool(name="square_root", description="Take the square root of a number", function=square_root),
    ]
    return Agent(tools=tools, max_steps=5)


def build_initial_state(prompt: str) -> State:
    return State(
        id=str(uuid.uuid4()),
        context=[{"role": "user", "content": prompt}],
        status="running",
    )


if __name__ == "__main__":
    agent = build_agent()
    initial_prompt = "Solve this equation: x^2 - 5x + 6 = 0"
    state = build_initial_state(initial_prompt)

    # Execute the agent
    state = agent.run(state)

    # Print results
    print("==== Run ====\n")
    print("ID:", state.id)
    print("Status:", state.status)
    print("Steps:", state.steps)
    print("Pending Tool Calls:", state.pending_tool_calls)
    print("Final Answer:", state.final_answer)
    # print(json.dumps(state.model_dump(), indent=2))

    # If we hit the step limit, continue running with the current state
    while state.status == "max_steps_reached":
        print("\n==== Continue (max_steps_reached) ====\n")
        state = agent.run(state)
        print("ID:", state.id)
        print("Status:", state.status)
        print("Steps:", state.steps)
        print("Pending Tool Calls:", state.pending_tool_calls)
        print("Final Answer:", state.final_answer)