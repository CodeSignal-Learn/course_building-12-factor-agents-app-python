import json

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
    max_steps=5
)

# Write the inital prompt
initial_prompt = "Solve this equation: x^2 - 5x + 6 = 0"

# Run the agent with the initial prompt
state = agent.run(initial_prompt)

# Print the final state
print("==== Launch ====\n")

print("ID:", state.id)
print("Status:", state.status)
print("Steps:", state.steps)
print("Pending Tool Calls:", state.pending_tool_calls)
print("Final Answer:", state.final_answer)
#print(json.dumps(state.model_dump(), indent=2))

if state.status != "complete":
    state = agent.resume(state)
    print("\n==== Resume ====\n")
    print("ID:", state.id)
    print("Status:", state.status)
    print("Steps:", state.steps)
    print("Pending Tool Calls:", state.pending_tool_calls)
    print("Final Answer:", state.final_answer)
    #print(json.dumps(state.model_dump(), indent=2))