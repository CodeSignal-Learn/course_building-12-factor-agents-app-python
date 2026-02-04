# Understanding the 12-Factor Agents Methodology

## Overview
Discover why reliable AI agents require more than delegating work to off‑the‑shelf frameworks. This foundational course introduces the 12‑Factor Agents methodology, distilling lessons that separate flashy demos from production systems. Learn how well‑engineered software augmented with targeted LLM integration—and twelve clear principles—yields maintainable, scalable, and trustworthy agentic apps.


## Outline
### Unit 1 - Why Principles Matter for Reliable Agent Systems
#### Goal
Understand the fundamental challenges of building production-ready AI agents and why principled approaches succeed where ad-hoc implementations fail. Students will learn about the "70-80% reliability wall" that most agent projects encounter, the limitations of existing frameworks, and how the 12-Factor Agents methodology addresses these systemic problems by bringing software engineering discipline to LLM-powered systems. The twelve factors are:
- Factor 1: Natural Language to Tool Calls
- Factor 2: Own your prompts
- Factor 3: Own your context window
- Factor 4: Tools are just structured outputs
- Factor 5: Unify execution state and business state
- Factor 6: Launch/Pause/Resume with simple APIs
- Factor 7: Contact humans with tool calls
- Factor 8: Own your control flow
- Factor 9: Compact Errors into Context Window
- Factor 10: Small, Focused Agents
- Factor 11: Trigger from anywhere, meet users where they are
- Factor 12: Make your agent a stateless reducer
### Unit 2 - Factors 1-4: Structure Prompts, Tools, and Context
#### Goal
Explore the foundational principles for controlling how LLMs interact with your system. Students will understand Factor 1 (Natural Language to Tool Calls) by learning how to translate user requests into machine-executable commands, Factor 2 (Own your prompts) by treating prompts as versioned artifacts rather than framework abstractions, Factor 3 (Own your context window) by explicitly managing what information flows through the agent's memory, and Factor 4 (Tools are just structured outputs) by understanding that function calls are simply validated JSON objects. Together, these factors establish the core discipline needed for agents that behave predictably and can be debugged when they fail.
### Unit 3 - Factors 5-8: Manage State and Control Flow
#### Goal
Learn the conceptual framework for designing agent systems where state is transparent and workflows remain under your control. Students will understand Factor 5 (Unify execution state and business state) by treating all agent interactions as part of the core application state, Factor 6 (Launch/Pause/Resume with simple APIs) by designing systems with well-defined lifecycle checkpoints, Factor 7 (Contact humans with tool calls) by making human escalation a first-class action within workflows, and Factor 8 (Own your control flow) by maintaining explicit loop management rather than delegating to frameworks. These factors are essential for production systems that handle real-world complexity and failure modes.
### Unit 4 - Factors 9-12: Keep Agents Small and Stateless
#### Goal
Grasp the architectural principles that make agents maintainable and scalable. Students will understand Factor 9 (Compact Errors into Context Window) by learning to feed execution failures back to the model for self-correction, Factor 10 (Small, Focused Agents) by creating minimal, single-responsibility components, Factor 11 (Trigger from anywhere, meet users where they are) by decoupling agent logic from any single interface, and Factor 12 (Make your agent a stateless reducer) by treating agents as pure functions that take state in and return state out. These factors are the keys to building systems that can grow in complexity while remaining debuggable, performant, and reliable at scale.

---

# Foundations of Agentic Tool Use in Python

## Overview
Master the practical building blocks of agentic systems in Python. Covering Factors 1, 3, 4, 8, and 9, you’ll prompt for structured outputs, define and validate tool schemas, own the context window, and run explicit loops that you control. You’ll also compact execution errors back into context for self-correction, turning natural language requests into reliable tool executions.


## Outline
### Unit 1 - Prompting LLMs for Structured Outputs
#### Goal
Prompting LLMs for Structured Outputs Goal: Teach how to prompt OpenAI models to return structured JSON outputs that can be reliably parsed and processed, grounding this in Factor 1 (Natural Language to Tool Calls) by having the model translate user requests into machine-executable, schema-shaped commands.

`main.py`
```python
import json
import openai

# Define the system prompt that instructs the model on its behavior
system_prompt = """
You are a helpful assistant that only answers with the following JSON schema:
{
    "answer": "the answer to the question"
}
"""

# Make a request to the Responses API
# The input is a list of messages, starting with the user's question
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=[
        {
            "role": "user",
            "content": "What is 15 + 27?"
        }
    ],
    reasoning={"effort": "low"}
)

# Parse the output to extract the JSON answer
for item in response.output:
    # Check if this item is a message
    if item.type == "message":
        try:
            # Extract raw text from the content
            text= item.content[0].text
            # Parse the JSON string from the content
            result = json.loads(text)
            # Extract and print the answer field
            print(f"Answer: {result['answer']}")
        except json.JSONDecodeError:
            # Handle cases where the model didn't return valid JSON
            print("Failed to parse JSON from response")
```
### Unit 2 - Defining a Tool Schema and Requiring Tool Use
#### Goal
Write a tool schema, provide it to the model, and handle the tool-call output, reinforcing Factor 4 (Tools are structured outputs) by parsing a validated JSON call and acting on it. Also see how to require tool use via `tool_choice="required"`.

`main.py`
```python
import json
import openai

# Define a single tool schema for final_answer
tool_schemas = [
    {
        "type": "function",
        "name": "final_answer",
        "description": "Provide the final answer and stop.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The final answer for the user."}
            },
            "required": ["answer"],
            "additionalProperties": False
        }
    }
]

system_prompt = """
You are a helpful assistant.
"""

response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=[
        {
            "role": "user",
            "content": "What is 15 + 27?"
        }
    ],
    tools=tool_schemas,
    tool_choice="required",
    reasoning={"effort": "low"}
)

# The model returns a function_call item with JSON arguments
for item in response.output:
    if item.type == "function_call" and item.name == "final_answer":
        args = json.loads(item.arguments)
        print(f"Answer: {args['answer']}")
```
### Unit 3 - Executing Tool Calls and Managing Context
#### Goal
Demonstrate executing function calls from model responses and feeding results back into the conversation context, introducing Factor 3 (Own your context window) by explicitly controlling what information flows through the agent's memory.

`main.py`
```python
import json
import openai

# Define the functions we want to make available to the model
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

# Map function names to actual function objects for execution
functions = {
    "add": add,
    "multiply": multiply
}

# Define tool schemas for the model (including final_answer)
tool_schemas = [
    {
        "type": "function",
        "name": "final_answer",
        "description": "Provide the final answer and stop.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The final answer for the user."}
            },
            "required": ["answer"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "add",
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "multiply",
        "description": "Multiply two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    }
]

system_prompt = """
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Initialize context with the user's message
# Context will grow as we add function calls and their results
context = [
    {
        "role": "user",
        "content": "Compute 15 + 27 and 8 * 11"
    }
]

# First API call: the model will see the user's request and available tools
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=context,
    tools=tool_schemas,
    tool_choice="required",
    reasoning={"effort": "low"}
)

# Process the response: execute any function calls and add results to context
# This is the key pattern: LLM calls functions -> we execute them -> we add results back to context
for item in response.output:
    if item.type == "function_call":
        # Step 1: Add the function call to context
        # This tells the model what function it decided to call (important for transparency)
        context.append({
            "type": "function_call",
            "name": item.name,
            "arguments": item.arguments,  # Keep as JSON string for storage
            "call_id": item.call_id  # Unique ID to match with the response
        })
        
        # Step 2: Execute the function call
        # Parse the JSON arguments and call the actual Python function
        args = json.loads(item.arguments)
        function = functions[item.name]
        result = function(**args)
        
        print(f"Executed {item.name}({args}) = {result}")
        
        # Step 3: Add the function result back to context
        # The model needs to see the result to continue its reasoning
        # Use the same call_id to link the result to the original call
        context.append({
            "type": "function_call_output",
            "call_id": item.call_id,  # Match with the function_call using call_id
            "output": json.dumps({"result": result})  # Result wrapped in JSON
        })

# Second API call: the model sees the function calls and their results
# It can now continue with the next step or provide a final answer
response = openai.responses.create(
    model="gpt-5",
    instructions=system_prompt,
    input=context,
    tools=tool_schemas,
    tool_choice="required",
    reasoning={"effort": "low"}
)

print("\nFinal response:")
print(response.output_text)
```
### Unit 4 - Controlling Loops of Agentic Tool-Use
#### Goal
Build an agentic loop that repeatedly calls the LLM, executes tools, and updates context until completion or max steps, implementing Factor 8 (Own your control flow) through explicit loop management and Factor 9 (Compact Errors into Context Window) by feeding execution failures back to the model.

`main.py`
```python
import json
import openai

# Define the functions we want to make available to the model
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

# Define tool schemas including a special final_answer tool
tool_schemas = [
    {
        "type": "function",
        "name": "add",
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "multiply",
        "description": "Multiply two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"}
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "final_answer",
        "description": "Provide the final answer and stop.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The final answer for the user."}
            },
            "required": ["answer"],
            "additionalProperties": False
        }
    }
]

system_prompt = """
You are a helpful assistant that can perform calculations.
When asked to do math, you must use the provided tools.
When your work is done, call the final_answer tool.
"""

# Initialize context with the user's message
context = [
    {
        "role": "user",
        "content": "What is 15 + 27? Then multiply the result by 3."
    }
]

# Set up loop control variables
max_steps = 10
step = 0
done = False
final_answer = None

# Main agent loop: continue until done or max steps reached
while not done and step < max_steps:
    step += 1
    print(f"\n--- Step {step} ---")
    
    # Call the LLM with current context
    response = openai.responses.create(
        model="gpt-5",
        instructions=system_prompt,
        input=context,
        tools=tool_schemas,
        tool_choice="required",
        reasoning={"effort": "low"}
    )
    
    # Process each item in the response output
    for item in response.output:
        if item.type == "function_call":
            function_name = item.name
            args = json.loads(item.arguments)
            
            print(f"Calling function: {function_name}({args})")
            
            # Add function call to context
            context.append({
                "type": "function_call",
                "name": function_name,
                "arguments": item.arguments,
                "call_id": item.call_id
            })
            
            # Execute tools with match/case (mirrors core/agent.py pattern)
            match function_name:
                case "final_answer":
                    final_answer = args.get("answer")
                    done = True
                    print(f"Final answer: {final_answer}")
                    break
                case "add":
                    try:
                        result = add(**args)
                        output = json.dumps({"result": result})
                        print(f"Result: {result}")
                    except Exception as e:
                        output = json.dumps({"error": str(e)})
                case "multiply":
                    try:
                        result = multiply(**args)
                        output = json.dumps({"result": result})
                        print(f"Result: {result}")
                    except Exception as e:
                        output = json.dumps({"error": str(e)})
                case _:
                    output = json.dumps({"error": f"Tool {function_name} not found"})

            if function_name != "final_answer":
                context.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": output
                })

if step >= max_steps:
    print(f"\nReached maximum steps ({max_steps})")

print(f"\nCompleted in {step} steps")
if final_answer:
    print(f"Final answer: {final_answer}")
```

---

# Developing a Stateless Agent in Python

## Overview
Turn scripts into reusable components by embracing stateless design. With Factors 2, 5, 6, 7, 10, and 12, you’ll externalize and version prompts, unify execution and business state, implement launch/pause/resume checkpoints, and make human escalation a first‑class tool. Compose small, single‑purpose agents and wrap logic as a stateless reducer that is easy to test and scale.


## Outline
### Unit 1 - Designing a Stateless Reducer Agent
#### Goal
Build a stateless reducer agent class with methods for LLM calls, tool execution, and step management (context in, context out), implementing Factor 12 (Make your agent a stateless reducer) by treating the agent as a pure function and Factor 10 (Small, Focused Agents) by creating a minimal, single-responsibility component ready to be composed into larger systems.

`src/core/agent.py`
```python
import json
import openai
from typing import List, Any, Optional

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        max_steps: int = 10,
        tools: Optional[List[ClientTool]] = None
    ):
        # Store configuration
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        
        # Prepare tools: create a lookup dictionary by name for fast access
        tools = tools or []
        self.tools = {tool.name: tool for tool in tools}
        
        # Extract schemas from tools for the LLM
        # The LLM needs schemas, not the actual tool objects
        self.tool_schemas = [tool.schema for tool in tools]
        
        # Add built-in final_answer tool
        # This is a special tool that signals the agent is done
        self.tool_schemas.append({
            "type": "function",
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        })

    def _call_llm(self, context: List[Any]):
        # Encapsulate the LLM API call
        # Takes context (list of messages/function calls) and returns response
        response = openai.responses.create(
            model=self.model,
            instructions="You are a helpful assistant. Always use tools. When done, call final_answer.",
            input=context,  # The conversation history
            tools=self.tool_schemas,  # Available tools for the model
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _call_tool(self, function_call: dict):
        # Execute a tool call and return the result in the expected format
        tool_name = function_call["name"]
        call_id = function_call["call_id"]
        tool_input = function_call["arguments"]  # Already a dict
        
        try:
            # Look up the tool and execute it
            result = self.tools[tool_name].execute(**tool_input)
        except KeyError:
            # Tool not found in our registry
            result = f"Error: Tool {tool_name} not found"
        except Exception as e:
            # Tool execution failed
            result = f"Error: {str(e)}"
        
        # Return result in the format expected by the Responses API
        return {
            "type": "function_call_output",
            "call_id": call_id,  # Match with the original call
            "output": json.dumps({"result": result})  # Must be JSON string
        }

    def _next_step(self, context: List[Any]):
        # Execute one step of the agent loop:
        # 1. Call LLM with current context
        # 2. Process function calls
        # 3. Execute tools and add results
        # Returns updated context, status, and final_answer
        
        response = self._call_llm(context)
        
        # Extract all function calls from the response
        function_calls = [item for item in response.output if item.type == "function_call"]
        
        # Process each function call
        for fc in function_calls:
            function_name = fc.name
            args = json.loads(fc.arguments)  # Parse JSON string to dict
            
            # Add function call to context (transparency)
            context.append({
                "type": "function_call",
                "name": function_name,
                "arguments": fc.arguments,  # Keep as JSON string
                "call_id": fc.call_id
            })
            
            # Check for completion signal
            if function_name == "final_answer":
                return context, "complete", args.get("answer")
            
            # Execute the tool and add result to context
            result = self._call_tool({
                "name": function_name,
                "arguments": args,
                "call_id": fc.call_id
            })
            context.append(result)
        
        # No final_answer yet, continue running
        return context, "running", None

    def run(self, context: List[Any]):
        # Main entry point: run the agent until done or max steps
        # This is the "reducer" pattern: context in, context out
        step = 0
        status = "running"
        final_answer = None
        
        # Loop until complete or max steps reached
        while status == "running" and step < self.max_steps:
            step += 1
            # Each step processes function calls and updates context
            context, status, final_answer = self._next_step(context)
            if final_answer:
                break  # Early exit if we got the answer
        
        # Handle max steps case
        if status == "running":
            status = "max_steps_reached"
        
        # Return the final state
        return context, status, final_answer
```

`src/main.py`
```python
from core.agent import Agent
from core.client_tool import ClientTool
from core.tools.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)

# Create ClientTool instances from math functions
# ClientTool automatically generates schemas from function signatures
tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

# Create agent with tools
agent = Agent(tools=tools, max_steps=10)

# Initialize context with user's request
context = [
    {
        "role": "user",
        "content": "What is 15 + 27? Then multiply the result by 3."
    }
]

# Run the agent: context in, context out (stateless reducer pattern)
context, status, final_answer = agent.run(context)

print(f"Status: {status}")
print(f"Final answer: {final_answer}")
```
### Unit 2 - Taking Ownership of our Prompts
#### Goal
Extract system prompts to external markdown files and load them dynamically, implementing Factor 2 (Own your prompts) by version-controlling prompts as first-class code rather than embedding them in framework abstractions.

`src/core/prompts/base_system.md`
```markdown
# ROLE
You are an autonomous agent that can take multiple tool-calling steps.

# REQUIREMENTS
- Do never output text, always ONLY call tools
- If your work is done, call the final_answer tool
- If you need to ask clarification to the user, use the ask_human tool
- ALWAYS prefer calling tools to compute, fetch, or transform information rather than fabricating results.

# EXTRA INSTRUCTIONS

```

`src/core/agent.py`
```python
import json
import openai
from typing import List, Any, Optional
from pathlib import Path

from core.client_tool import ClientTool

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "None",
        max_steps: int = 10,
        tools: Optional[List[ClientTool]] = None
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        # Load system prompt from markdown file (Factor 2: Own your prompts)
        # Using Path ensures it works regardless of where the script is run from
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions
        tools = tools or []
        self.tools = {tool.name: tool for tool in tools}
        self.tool_schemas = [tool.schema for tool in tools]
        self.tool_schemas.append({
            "type": "function",
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        })

    def _call_llm(self, context: List[Any]):
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _call_tool(self, function_call: dict):
        tool_name = function_call["name"]
        call_id = function_call["call_id"]
        tool_input = function_call["arguments"]
        
        try:
            result = self.tools[tool_name].execute(**tool_input)
        except KeyError:
            result = f"Error: Tool {tool_name} not found"
        except Exception as e:
            result = f"Error: {str(e)}"
        
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps({"result": result})
        }

    def _next_step(self, context: List[Any]):
        response = self._call_llm(context)
        
        function_calls = [item for item in response.output if item.type == "function_call"]
        
        for fc in function_calls:
            function_name = fc.name
            args = json.loads(fc.arguments)
            
            context.append({
                "type": "function_call",
                "name": function_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })
            
            if function_name == "final_answer":
                return context, "complete", args.get("answer")
            
            result = self._call_tool({
                "name": function_name,
                "arguments": args,
                "call_id": fc.call_id
            })
            context.append(result)
        
        return context, "running", None

    def run(self, context: List[Any]):
        step = 0
        status = "running"
        final_answer = None
        
        while status == "running" and step < self.max_steps:
            step += 1
            context, status, final_answer = self._next_step(context)
            if final_answer:
                break
        
        if status == "running":
            status = "max_steps_reached"
        
        return context, status, final_answer
```
### Unit 3 - Unifying Execution and Business States
#### Goal
Create a unified State class that combines execution state (steps, status) with business state (context, final_answer) for pause/resume capabilities, implementing Factor 5 (Unify execution state and business state) by treating all agent interactions as part of the core application state.

`src/core/models/state.py`
```python
from typing import List, Any, Optional
from pydantic import BaseModel, Field

# State class unifies execution state and business state (Factor 5)
# This allows us to pause/resume, track progress, and manage errors in one place
class State(BaseModel):
    id: str  # Unique identifier for this execution
    steps: int = 0  # Number of steps executed so far
    status: str = "running"  # Current status: "running", "complete", "waiting_human_input", "max_steps_reached"
    context: List[Any] = Field(default_factory=list)  # Conversation history: messages, function calls, results
    pending_tool_calls: List[Any] = Field(default_factory=list)  # Function calls waiting to be executed
    error: Optional[str] = None  # Error message if something went wrong
    final_answer: Optional[str] = None  # The final answer when complete
```

`src/core/agent.py`
```python
import json
import openai
from typing import List, Any, Optional
from pathlib import Path

from core.models.state import State

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "None",
        max_steps: int = 10,
        tools: Optional[List[ClientTool]] = None
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        # Load system prompt from markdown file (Factor 2: Own your prompts)
        # Using Path ensures it works regardless of where the script is run from
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions
        tools = tools or []
        self.tools = {tool.name: tool for tool in tools}
        self.tool_schemas = [tool.schema for tool in tools]
        self.tool_schemas.append({
            "type": "function",
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        })

    def _call_llm(self, context: List[Any]):
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _call_tool(self, function_call: dict):
        tool_name = function_call["name"]
        call_id = function_call["call_id"]
        tool_input = function_call["arguments"]
        
        try:
            result = self.tools[tool_name].execute(**tool_input)
        except KeyError:
            result = f"Error: Tool {tool_name} not found"
        except Exception as e:
            result = f"Error: {str(e)}"
        
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps({"result": result})
        }

    def _next_step(self, state: State):
        # Execute one step: process pending tool calls, then call LLM for new ones
        state.steps += 1
        
        # Process all pending tool calls from previous step
        # Use list() to create a copy so we can safely remove items during iteration
        for function_call in list(state.pending_tool_calls):
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]  # Already a dict
            call_id = function_call["call_id"]
            
            # Add function call to context for transparency
            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),  # Serialize to JSON string for storage
                "call_id": call_id
            })
            
            # Handle special control tools
            if call_name == "final_answer":
                # Agent is done, clear pending calls and set status
                state.pending_tool_calls = []
                state.status = "complete"
                state.final_answer = call_arguments.get("answer")
                return state
            
            # Execute regular tool and add result to context
            result = self._call_tool({
                "name": call_name,
                "arguments": call_arguments,
                "call_id": call_id
            })
            state.pending_tool_calls.remove(function_call)
            state.context.append(result)
        
        # Call LLM with updated context (includes tool results)
        response = self._call_llm(state.context)
        
        # Extract new function calls from LLM response
        function_calls = [item for item in response.output if item.type == "function_call"]
        
        # Convert SDK objects to plain dicts for storage in state
        function_call_dicts = [
            {
                "name": fc.name,
                "arguments": json.loads(fc.arguments),  # Parse JSON string to dict
                "call_id": fc.call_id,
                "type": fc.type
            }
            for fc in function_calls
        ]
        
        # Add new function calls to pending list (will be processed in next step)
        state.pending_tool_calls.extend(function_call_dicts)
        return state

    def run(self, state: State):
        # Main entry point: run agent until complete or max steps
        # State is mutated in place (unified execution and business state)
        state.status = "running"
        
        # Loop until complete or max steps reached
        while state.status == "running" and state.steps < self.max_steps:
            state = self._next_step(state)
        
        # Handle max steps case
        if state.status == "running":
            state.status = "max_steps_reached"
        
        return state
```

`src/main.py`
```python
import uuid
from core.agent import Agent
from core.models.state import State
from core.client_tool import ClientTool
from core.tools.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)

tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

agent = Agent(tools=tools, max_steps=10)

# Create initial state with unique ID
# State unifies execution state (steps, status) with business state (context, final_answer)
state = State(
    id=str(uuid.uuid4()),  # Unique identifier for this execution
    context=[
        {
            "role": "user",
            "content": "What is 15 + 27? Then multiply the result by 3."
        }
    ],
    status="running"  # Initial status
)

# Run the agent: state is modified in place
state = agent.run(state)

print(f"ID: {state.id}")
print(f"Status: {state.status}")
print(f"Steps: {state.steps}")
print(f"Final answer: {state.final_answer}")
```
### Unit 4 - Resuming Executions from Previous States
#### Goal
Demonstrate resuming agent execution from a saved state, enabling pause/resume functionality after interruptions and implementing Factor 6 (Launch/Pause/Resume with simple APIs) by designing agent logic that can be stopped and safely resumed at well-defined checkpoints.

`src/main.py`
```python
import json
import uuid
from core.agent import Agent
from core.models.state import State

def add(a: float, b: float) -> float:
    return a + b

def multiply(a: float, b: float) -> float:
    return a * b

tools = [
    {
        "name": "add",
        "description": "Add two numbers together",
        "function": add,
        "schema": {
            "type": "function",
            "name": "add",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"}
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "name": "multiply",
        "description": "Multiply two numbers together",
        "function": multiply,
        "schema": {
            "type": "function",
            "name": "multiply",
            "description": "Multiply two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"}
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    }
]

agent = Agent(tools=tools, max_steps=3)

state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "What is 15 + 27? Then multiply the result by 3."
        }
    ],
    status="running"
)

# Run the agent (may hit max_steps limit)
state = agent.run(state)
print(f"After first run - Status: {state.status}, Steps: {state.steps}")

# If we hit max_steps, we can resume with the same state
# The state contains all the context needed to continue
if state.status == "max_steps_reached":
    print("Resuming execution...")
    # Resume from where we left off - state has all the context
    state = agent.run(state)
    print(f"After resume - Status: {state.status}, Steps: {state.steps}")

print(f"Final answer: {state.final_answer}")
```
### Unit 5 - Contacting Humans Using Tool Calls
#### Goal
Add an ask_human tool that pauses execution and waits for user input before resuming, implementing Factor 7 (Contact humans with tool calls) by making human escalation a first-class action within the agent's workflow.

`src/utils/human_interaction.py`
```python
import json

# Helper function to handle human interaction via CLI
# This implements Factor 7: Contact humans with tool calls
def ask_human_cli(function_call: dict) -> dict:
    # Parse the question from the function call arguments
    arguments = json.loads(function_call['arguments'])
    try:
        # Prompt the user and get their response
        response = input(f"\nAgent is asking: {arguments['question']}\n> ")
        # Return the response in the format expected by the Responses API
        return {
            "type": "function_call_output",
            "call_id": function_call["call_id"],  # Match with the original call
            "output": json.dumps({
                "answer": response  # Wrap answer in JSON
            })
        }
    except EOFError:
        # Handle non-interactive environments (like automated tests)
        raise EOFError("Cannot request clarification in non-interactive environment")
```

`src/core/agent.py`
```python
import json
import openai
from typing import List, Any, Optional
from pathlib import Path

from core.models.state import State

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "None",
        max_steps: int = 10,
        tools: Optional[List[ClientTool]] = None
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        # Load system prompt from markdown file (Factor 2: Own your prompts)
        # Using Path ensures it works regardless of where the script is run from
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions
        tools = tools or []
        self.tools = {tool.name: tool for tool in tools}
        self.tool_schemas = [tool.schema for tool in tools]
        self.tool_schemas.append({
            "type": "function",
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        })
        self.tool_schemas.append({
            "type": "function",
            "name": "ask_human",
            "description": "Ask the user for clarification or additional information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question or prompt to ask the user"}
                },
                "required": ["question"],
                "additionalProperties": False
            }
        })

    def _call_llm(self, context: List[Any]):
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _call_tool(self, function_call: dict):
        tool_name = function_call["name"]
        call_id = function_call["call_id"]
        tool_input = function_call["arguments"]
        
        try:
            result = self.tools[tool_name].execute(**tool_input)
        except KeyError:
            result = f"Error: Tool {tool_name} not found"
        except Exception as e:
            result = f"Error: {str(e)}"
        
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps({"result": result})
        }

    def _next_step(self, state: State):
        state.steps += 1
        
        for function_call in list(state.pending_tool_calls):
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]
            call_id = function_call["call_id"]
            
            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),
                "call_id": call_id
            })
            
            # Handle ask_human tool (Factor 7: Contact humans with tool calls)
            if call_name == "ask_human":
                # Don't execute the tool here - wait for human input
                state.pending_tool_calls.remove(function_call)
                state.status = "waiting_human_input"  # Signal that we're waiting
                return state  # Stop execution until human responds
            
            if call_name == "final_answer":
                state.pending_tool_calls = []
                state.status = "complete"
                state.final_answer = call_arguments.get("answer")
                return state
            
            result = self._call_tool({
                "name": call_name,
                "arguments": call_arguments,
                "call_id": call_id
            })
            state.pending_tool_calls.remove(function_call)
            state.context.append(result)
        
        response = self._call_llm(state.context)
        
        function_calls = [item for item in response.output if item.type == "function_call"]
        function_call_dicts = [
            {
                "name": fc.name,
                "arguments": json.loads(fc.arguments),
                "call_id": fc.call_id,
                "type": fc.type
            }
            for fc in function_calls
        ]
        
        state.pending_tool_calls.extend(function_call_dicts)
        return state

    def run(self, state: State):
        state.status = "running"
        
        while state.status == "running" and state.steps < self.max_steps:
            state = self._next_step(state)
        
        if state.status == "running":
            state.status = "max_steps_reached"
        
        return state
```

`src/main.py`
```python
import uuid
from core.agent import Agent
from core.models.state import State
from core.client_tool import ClientTool
from core.tools.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)
from utils.human_interaction import ask_human_cli

tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

agent = Agent(tools=tools, max_steps=10)

state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "What is 15 + 27? Ask me for my name first."
        }
    ],
    status="running"
)

# Run the agent until it needs human input or completes
state = agent.run(state)

# Handle human interaction loop
# When agent calls ask_human, status becomes "waiting_human_input"
while state.status == "waiting_human_input":
    print(f"\nStatus: {state.status}, Steps: {state.steps}")
    
    # Get the last function call (should be ask_human)
    function_call = state.context[-1]
    # Ask the user and get their response
    answer = ask_human_cli(function_call)
    # Add the human's answer to context
    state.context.append(answer)
    
    # Resume agent execution with the human's input
    state = agent.run(state)

print(f"\nFinal Status: {state.status}")
print(f"Final Answer: {state.final_answer}")
```

---

# Exposing Agents with Simple APIs in Python

## Overview
Expose agents as services reachable from any interface. With Factors 5, 6, 7, and 11, you’ll persist unified state in a database, orchestrate runs via background tasks and REST endpoints, and add pause/resume controls. Wire human responses back into waiting workflows and decouple triggers from UI so web apps, bots, and systems can launch, monitor, and resume runs at scale.


## Outline
### Unit 1 - Launching Agents with RESTful APIs
#### Goal
Build a FastAPI server with endpoints to launch agents and retrieve state, using in-memory storage and background tasks. By decoupling agent logic from any single interface and exposing it via REST APIs, this unit implements Factor 11 (Trigger from anywhere, meet users where they are).

`src/server/main.py`
```python
import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent
from core.client_tool import ClientTool
from core.tools.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)

# Create tools
tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

# Create agent
agent = Agent(tools=tools, max_steps=10)

# In-memory storage (will be replaced with database in next unit)
# Using a simple dictionary to store states by ID
states: Dict[str, State] = {}

app = FastAPI()

class LaunchRequest(BaseModel):
    input_prompt: str

def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread (non-blocking)"""
    # Get state from memory
    state = states[state_id]
    # Run the agent (this may take time)
    state = agent.run(state)
    # Update stored state with result
    states[state_id] = state

@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
    # Create initial state with unique ID
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )
    
    # Store in memory
    states[initial_state.id] = initial_state
    
    # Run agent in background (non-blocking)
    # This allows the API to return immediately while agent runs
    background_tasks.add_task(_run_agent_in_background, initial_state.id)
    
    return initial_state

@app.get("/agent/state/{state_id}", response_model=State)
def get_state(state_id: str):
    """Get the current state by ID"""
    if state_id not in states:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="State not found")
    return states[state_id]
```

`main.py`
```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Launch a new agent
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "What is 15 + 27? Then multiply the result by 3."}
)
state = response.json()
print(f"Launched agent with ID: {state['id']}")

# Poll for the result
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()
    print(f"Status: {current_state['status']}, Steps: {current_state['steps']}")
    
    if current_state['status'] in ["complete", "max_steps_reached", "failed"]:
        print(f"Final answer: {current_state.get('final_answer')}")
        break
    
    time.sleep(1)
```
### Unit 2 - Persisting States with Databases and Callbacks
#### Goal
Replace in-memory storage with SQLite database and add progress callbacks to persist state after each agent step, building on earlier factors to create a production-ready persistence layer.

`src/server/database.py`
```python
import json
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from core.models.state import State

Base = declarative_base()

# SQLAlchemy model for storing State in the database
class StateModel(Base):
    __tablename__ = "states"
    
    id = Column(String, primary_key=True)
    steps = Column(Integer, default=0)
    status = Column(String, default="running")
    context = Column(JSON, default=list)
    pending_tool_calls = Column(JSON, default=list)
    error = Column(Text, nullable=True)
    final_answer = Column(Text, nullable=True)

# SQLite database (file-based, perfect for development)
db_path = Path(__file__).resolve().parent.parent / "data" / "agent_states.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{db_path}", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def pydantic_to_db(state: State) -> StateModel:
    """Convert Pydantic State to database model"""
    return StateModel(
        id=state.id,
        steps=state.steps,
        status=state.status,
        context=state.context,
        pending_tool_calls=state.pending_tool_calls,
        error=state.error,
        final_answer=state.final_answer,
    )

def db_to_pydantic(db_state: StateModel) -> State:
    """Convert database model to Pydantic State"""
    return State(
        id=db_state.id,
        steps=db_state.steps,
        status=db_state.status,
        context=db_state.context or [],
        pending_tool_calls=db_state.pending_tool_calls or [],
        error=db_state.error,
        final_answer=db_state.final_answer,
    )

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

`src/core/agent.py`
```python
import json
import openai
from typing import List, Any, Optional
from pathlib import Path

from core.models.state import State
from core.client_tool import ClientTool

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "None",
        max_steps: int = 10,
        tools: Optional[List[ClientTool]] = None
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        # Load system prompt from markdown file (Factor 2: Own your prompts)
        # Using Path ensures it works regardless of where the script is run from
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions
        self.max_steps = max_steps
        tools = tools or []
        self.tools = {tool.name: tool for tool in tools}
        self.tool_schemas = [tool.schema for tool in tools]
        # Add built-in final_answer tool
        self.tool_schemas.append({
            "type": "function",
            "name": "final_answer",
            "description": "Provide the final answer and stop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "The final answer for the user."}
                },
                "required": ["answer"],
                "additionalProperties": False
            }
        })
        # Add built-in ask_human tool
        self.tool_schemas.append({
            "type": "function",
            "name": "ask_human",
            "description": "Ask the user for clarification or additional information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question or prompt to ask the user"}
                },
                "required": ["question"],
                "additionalProperties": False
            }
        })

    def _call_llm(self, context: List[Any]):
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _call_tool(self, function_call: dict):
        # Execute a tool call and return the result in the expected format
        tool_name = function_call["name"]
        call_id = function_call["call_id"]
        tool_input = function_call["arguments"]  # Already a dict
        
        try:
            # Look up the tool and execute it
            result = self.tools[tool_name].execute(**tool_input)
        except KeyError:
            # Tool not found in our registry
            result = f"Error: Tool {tool_name} not found"
        except Exception as e:
            # Tool execution failed
            result = f"Error: {str(e)}"
        
        # Return result in the format expected by the Responses API
        return {
            "type": "function_call_output",
            "call_id": call_id,  # Match with the original call
            "output": json.dumps({"result": result})  # Must be JSON string
        }

    def _next_step(self, state: State):
        # Execute one step: process pending tool calls, then call LLM for new ones
        state.steps += 1
        
        # Process all pending tool calls from previous step
        # Use list() to create a copy so we can safely remove items during iteration
        for function_call in list(state.pending_tool_calls):
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]  # Already a dict
            call_id = function_call["call_id"]
            
            # Add function call to context for transparency
            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),  # Serialize to JSON string for storage
                "call_id": call_id
            })
            
            # Handle ask_human tool (Factor 7: Contact humans with tool calls)
            if call_name == "ask_human":
                # Don't execute the tool here - wait for human input
                state.pending_tool_calls.remove(function_call)
                state.status = "waiting_human_input"  # Signal that we're waiting
                return state  # Stop execution until human responds
            
            # Handle special control tools
            if call_name == "final_answer":
                # Agent is done, clear pending calls and set status
                state.pending_tool_calls = []
                state.status = "complete"
                state.final_answer = call_arguments.get("answer")
                return state
            
            # Execute regular tool and add result to context
            result = self._call_tool({
                "name": call_name,
                "arguments": call_arguments,
                "call_id": call_id
            })
            state.pending_tool_calls.remove(function_call)
            state.context.append(result)
        
        # Call LLM with updated context (includes tool results)
        response = self._call_llm(state.context)
        
        # Extract new function calls from LLM response
        function_calls = [item for item in response.output if item.type == "function_call"]
        
        # Convert SDK objects to plain dicts for storage in state
        function_call_dicts = [
            {
                "name": fc.name,
                "arguments": json.loads(fc.arguments),  # Parse JSON string to dict
                "call_id": fc.call_id,
                "type": fc.type
            }
            for fc in function_calls
        ]
        
        # Add new function calls to pending list (will be processed in next step)
        state.pending_tool_calls.extend(function_call_dicts)
        return state

    def run(self, state: State, progress_callback=None):
        """
        Execute agent steps on a given state.
        The state should already be initialized with context and status.
        If state is paused/waiting, it will be set to running and execution will continue.
        
        Args:
            state: The state to run
            progress_callback: Optional callback(state) called after each step
        """
        # Ensure state is set to running
        state.status = "running"
        
        # Calculate max steps: if resuming (steps > 0), allow continuing from current step count
        is_resuming = state.steps > 0
        max_steps_allowed = (self.max_steps + state.steps) if is_resuming else self.max_steps
        
        # Call next step until complete or waiting_human_input
        while state.status == "running" and state.steps < max_steps_allowed:
            state = self._next_step(state)
            # Call progress callback if provided (allows saving state after each step)
            if progress_callback:
                progress_callback(state)
        
        # If still running and max steps reached, set status to max_steps_reached
        if state.status == "running" and state.steps >= max_steps_allowed:
            state.status = "max_steps_reached"
        
        return state
```

`src/server/main.py`
```python
import uuid
from fastapi import FastAPI, BackgroundTasks
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
    square_root
)
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

# Create tools
tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

# Create agent
agent = Agent(tools=tools, max_steps=10)

app = FastAPI()

class LaunchRequest(BaseModel):
    input_prompt: str

def _create_progress_callback(state_id: str):
    """Create a progress callback function that saves state after each step"""
    # This callback is called by the agent after each step
    # It ensures state is persisted to the database incrementally
    def save_progress(state: State):
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                # Update all fields with current state
                # This allows clients to see progress in real-time
                db_state.steps = state.steps
                db_state.status = state.status
                db_state.context = state.context
                db_state.pending_tool_calls = state.pending_tool_calls
                db_state.error = state.error
                db_state.final_answer = state.final_answer
                session.commit()
    return save_progress

def _run_agent_in_background(state_id: str):
    """Run the agent in a background thread and update the database"""
    # Load state from database
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
        if not db_state:
            return
        # Convert database model to Pydantic State
        working_state = db_to_pydantic(db_state)
    
    # Run agent with progress callback to save state after each step
    # The callback allows clients to poll and see progress in real-time
    save_progress = _create_progress_callback(state_id)
    final_state = agent.run(working_state, progress_callback=save_progress)
    
    # Final save to ensure everything is persisted
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

@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
    # Create initial state
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )
    
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
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="State not found")
        return db_to_pydantic(db_state)
```
### Unit 3 - Pausing and Resuming Agents Through API Calls
#### Goal
Add API endpoints to pause running agents and resume paused agents, applying the pause/resume patterns introduced earlier to a real API interface with lifecycle controls.

`src/server/main.py`
```python
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
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
    square_root
)
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

agent = Agent(tools=tools, max_steps=10)

app = FastAPI()

class LaunchRequest(BaseModel):
    input_prompt: str

class PauseRequest(BaseModel):
    id: str

class ResumeRequest(BaseModel):
    id: str

def _create_progress_callback(state_id: str):
    """Create a progress callback function that saves state after each step"""
    def save_progress(state: State):
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                # Check if status was changed to "paused" externally (via pause endpoint)
                if db_state.status == "paused":
                    # Update local state to paused so agent loop will exit
                    state.status = "paused"
                    # Don't overwrite the paused status - just save other fields
                    # This allows pause to work by checking DB status in callback
                    db_state.steps = state.steps
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
                else:
                    # Normal save - update all fields including status
                    db_state.steps = state.steps
                    db_state.status = state.status
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
                session.commit()
    return save_progress

def _run_agent_in_background(state_id: str, working_state: Optional[State] = None):
    """Run the agent in a background thread and update the database"""
    # If working_state not provided, load from database
    if working_state is None:
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if not db_state:
                return
            db_state.status = "running"
            session.commit()
            working_state = db_to_pydantic(db_state)
    else:
        # working_state provided (for resume), ensure DB status is running
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                db_state.status = "running"
                session.commit()
    
    # Run agent with progress callback
    save_progress = _create_progress_callback(state_id)
    final_state = agent.run(working_state, progress_callback=save_progress)
    
    # Final update
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

@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )
    
    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)
        session.commit()
    
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

@app.post("/agent/pause", response_model=State)
def agent_pause(payload: PauseRequest):
    """Pause a running agent workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        # Only allow pausing if agent is currently running
        if db_state.status != "running":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause agent. Current status: {db_state.status}"
            )
        
        # Set status to paused (progress callback will detect this and stop the loop)
        db_state.status = "paused"
        session.commit()
        
        return db_to_pydantic(db_state)

@app.post("/agent/resume", response_model=State)
def agent_resume(payload: ResumeRequest, background_tasks: BackgroundTasks):
    """Resume a paused or interrupted workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        # Prevent concurrent execution
        if db_state.status == "running":
            raise HTTPException(status_code=409, detail="Agent is already running")
        
        # Convert to Pydantic
        working_state = db_to_pydantic(db_state)
    
    # Run agent in background (non-blocking)
    background_tasks.add_task(_run_agent_in_background, payload.id, working_state)
    
    return working_state
```

`main.py`
```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Launch a new agent
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "What is 15 + 27? Then multiply the result by 3."}
)
state = response.json()
print(f"Launched agent with ID: {state['id']}")

# Wait a bit
time.sleep(2)

# Pause the agent
response = requests.post(
    f"{BASE_URL}/agent/pause",
    json={"id": state['id']}
)
paused_state = response.json()
print(f"Paused agent. Status: {paused_state['status']}, Steps: {paused_state['steps']}")

# Resume the agent
response = requests.post(
    f"{BASE_URL}/agent/resume",
    json={"id": state['id']}
)
resumed_state = response.json()
print(f"Resumed agent. Status: {resumed_state['status']}")

# Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()
    print(f"Status: {current_state['status']}, Steps: {current_state['steps']}")
    
    if current_state['status'] in ["complete", "max_steps_reached", "failed"]:
        print(f"Final answer: {current_state.get('final_answer')}")
        break
    
    time.sleep(1)
```
### Unit 4 - Integrating Human Input Back to Agents
#### Goal
Create an API endpoint that accepts human input for waiting agents and automatically resumes execution with the response, completing the human-in-the-loop workflow by wiring user answers back into the agent's context.

`src/server/main.py`
```python
import json
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
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
    square_root
)
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

tools = [
    ClientTool(name="sum_numbers", description="Sum two numbers", function=sum_numbers),
    ClientTool(name="multiply_numbers", description="Multiply two numbers", function=multiply_numbers),
    ClientTool(name="subtract_numbers", description="Subtract two numbers", function=subtract_numbers),
    ClientTool(name="divide_numbers", description="Divide two numbers", function=divide_numbers),
    ClientTool(name="power", description="Raise a number to a power", function=power),
    ClientTool(name="square_root", description="Take the square root of a number", function=square_root)
]

agent = Agent(tools=tools, max_steps=10)

app = FastAPI()

class LaunchRequest(BaseModel):
    input_prompt: str

class PauseRequest(BaseModel):
    id: str

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
                if db_state.status == "paused":
                    state.status = "paused"
                    db_state.steps = state.steps
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
                else:
                    db_state.steps = state.steps
                    db_state.status = state.status
                    db_state.context = state.context
                    db_state.pending_tool_calls = state.pending_tool_calls
                    db_state.error = state.error
                    db_state.final_answer = state.final_answer
                session.commit()
    return save_progress

def _get_call_id_from_state(state: State) -> Optional[str]:
    """Extract the call_id from the last ask_human call in context"""
    # Search backwards through context to find the most recent ask_human call
    # We need the call_id to match the human's response with the original call
    for item in reversed(state.context):
        if isinstance(item, dict) and item.get("type") == "function_call" and item.get("name") == "ask_human":
            return item.get("call_id")
    return None

def _run_agent_in_background(state_id: str, working_state: Optional[State] = None):
    """Run the agent in a background thread and update the database"""
    if working_state is None:
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if not db_state:
                return
            db_state.status = "running"
            session.commit()
            working_state = db_to_pydantic(db_state)
    else:
        with get_db_session() as session:
            db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
            if db_state:
                db_state.status = "running"
                session.commit()
    
    save_progress = _create_progress_callback(state_id)
    final_state = agent.run(working_state, progress_callback=save_progress)
    
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

@app.post("/agent/launch", response_model=State)
def agent_launch(payload: LaunchRequest, background_tasks: BackgroundTasks):
    """Launch a new agent workflow"""
    initial_state = State(
        id=str(uuid.uuid4()),
        context=[
            {
                "role": "user",
                "content": payload.input_prompt
            }
        ],
        status="running"
    )
    
    with get_db_session() as session:
        db_state = pydantic_to_db(initial_state)
        session.add(db_state)
        session.commit()
    
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

@app.post("/agent/pause", response_model=State)
def agent_pause(payload: PauseRequest):
    """Pause a running agent workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        if db_state.status != "running":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pause agent. Current status: {db_state.status}"
            )
        
        db_state.status = "paused"
        session.commit()
        return db_to_pydantic(db_state)

@app.post("/agent/resume", response_model=State)
def agent_resume(payload: ResumeRequest, background_tasks: BackgroundTasks):
    """Resume a paused or interrupted workflow"""
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        if not db_state:
            raise HTTPException(status_code=404, detail="State not found")
        
        if db_state.status == "running":
            raise HTTPException(status_code=409, detail="Agent is already running")
        
        working_state = db_to_pydantic(db_state)
    
    background_tasks.add_task(_run_agent_in_background, payload.id, working_state)
    return working_state

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
    # This matches the human's answer to the original ask_human function call
    call_id = _get_call_id_from_state(working_state)
    if not call_id:
        raise HTTPException(
            status_code=400,
            detail="Could not find ask_human call in state context"
        )
    
    # Add the human's answer as a function_call_output to context
    # Format matches what the Responses API expects
    human_response = {
        "type": "function_call_output",
        "call_id": call_id,  # Match with the original ask_human call
        "output": json.dumps({"answer": payload.answer})  # Wrap answer in JSON
    }
    working_state.context.append(human_response)
    
    # Update state in database with new context
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == payload.id).first()
        db_state.context = working_state.context
        db_state.status = "running"  # Change status back to running so agent can continue
        session.commit()
    
    # Run agent in background (non-blocking)
    # Pass working_state so agent continues with the human's input
    background_tasks.add_task(_run_agent_in_background, payload.id, working_state)
    
    return working_state
```

`main.py`
```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Launch a new agent that will ask for human input
response = requests.post(
    f"{BASE_URL}/agent/launch",
    json={"input_prompt": "What is 15 + 27? Ask me for my name first."}
)
state = response.json()
print(f"Launched agent with ID: {state['id']}")

# Poll until it's waiting for human input
while True:
    response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
    current_state = response.json()
    print(f"Status: {current_state['status']}, Steps: {current_state['steps']}")
    
    if current_state['status'] == "waiting_human_input":
        print("Agent is waiting for human input!")
        break
    
    if current_state['status'] in ["complete", "max_steps_reached", "failed"]:
        print(f"Completed: {current_state.get('final_answer')}")
        break
    
    time.sleep(1)

# Provide human input
if current_state['status'] == "waiting_human_input":
    response = requests.post(
        f"{BASE_URL}/agent/provide_input",
        json={"id": state['id'], "answer": "Matheus"}
    )
    print("Provided input, agent resuming...")
    
    # Poll for completion
    while True:
        response = requests.get(f"{BASE_URL}/agent/state/{state['id']}")
        current_state = response.json()
        print(f"Status: {current_state['status']}, Steps: {current_state['steps']}")
        
        if current_state['status'] in ["complete", "max_steps_reached", "failed"]:
            print(f"Final answer: {current_state.get('final_answer')}")
            break
        
        time.sleep(1)
```
### Unit 5 - Controlling Agents from an Accessible Client
#### Goal
Demonstrate using a web-based UI client to interact with the agent API, showing how the same agent logic can be accessed from different interfaces and channels.
