# Course 1: Understanding the 12-Factor Agents Methodology

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

# Course 2: Foundations of Agentic Tool Use in Python

## Overview
Master the practical building blocks of agentic systems in Python. Covering Factors 1, 3, 4, 8, and 9, you’ll prompt for structured outputs, define and validate tool schemas, own the context window, and run explicit loops that you control. You’ll also compact execution errors back into context for self-correction, turning natural language requests into reliable tool executions.


## Outline
### Unit 1 - Prompting LLMs for Structured Outputs
#### Goal
Prompting LLMs for Structured Outputs Goal: Teach how to prompt OpenAI models to return structured JSON outputs that can be reliably parsed and processed, grounding this in Factor 1 (Natural Language to Tool Calls) by having the model translate user requests into machine-executable, schema-shaped commands.

#### Files

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

#### Files

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

#### Files

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

#### Files

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

# Course 3: Developing a Stateless Agent in Python

## Overview
Turn scripts into reusable components by embracing stateless design. With Factors 2, 5, 10, and 12, you’ll externalize prompts, unify execution and business state, and build a reducer-style agent that takes state in and returns state out.


## Outline
### Unit 1 - Designing a Stateless Reducer Agent
#### Goal
Build an Agent that processes context lists, executes tools via `match/case`, and returns updated context. This implements Factor 12 (stateless reducer) and Factor 10 (small, focused agent). We keep prompts inline for now and introduce prompt files in Unit 2.

#### Files

`src/core/agent.py`
```python
import json
import openai
from pathlib import Path
from typing import List, Any

from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)
class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        # Keep prompt inline in Unit 1; Unit 2 externalizes it.
        self.system_prompt = (
            "You are a helpful assistant. "
            "When your work is done, call the final_answer tool. "
            "Prefer using tools to compute or transform results."
        ) + extra_instructions

        # Load tool schemas from JSON files.
        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]

    def _call_llm(self, context: List[Any]):
        # Pass full context directly in Unit 1.
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _next_step(self, context: List[Any]):
        # One step: ask the model for tool calls, then execute them.
        response = self._call_llm(context)
        function_calls = [item for item in response.output if item.type == "function_call"]

        for fc in function_calls:
            call_name = fc.name
            call_arguments = json.loads(fc.arguments)

            context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })

            if call_name == "final_answer":
                # Stop when the model signals completion.
                return context, "complete", call_arguments.get("answer")

            # Execute the requested tool and capture its output.
            match call_name:
                case "sum_numbers":
                    try:
                        result = sum_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "multiply_numbers":
                    try:
                        result = multiply_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "subtract_numbers":
                    try:
                        result = subtract_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "divide_numbers":
                    try:
                        result = divide_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "power":
                    try:
                        result = power(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "square_root":
                    try:
                        result = square_root(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case _:
                    output = json.dumps({"result": f"Error: Tool {call_name} not found"})

            context.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": output
            })

        # No completion yet; keep running.
        return context, "running", None

    def run(self, context: List[Any]):
        # Reducer loop: context in, context out.
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
        # Handle max steps case
        if status == "running":
            status = "max_steps_reached"

        # Return the final state
        return context, status, final_answer
```

`src/main.py`
```python
from core.agent import Agent

agent = Agent(max_steps=10)

context = [
    {
        "role": "user",
        "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
    }
]

context, status, final_answer = agent.run(context)

print(f"Status: {status}")
print(f"Final answer: {final_answer}")
```
`src/core/tools/schemas/math.json`
```json
[
  {
    "type": "function",
    "name": "sum_numbers",
    "description": "Sum two numbers",
    "parameters": {
      "type": "object",
      "properties": {
        "a": { "type": "number", "description": "The first number" },
        "b": { "type": "number", "description": "The second number" }
      },
      "required": ["a", "b"],
      "additionalProperties": false
    }
  },
  {
    "type": "function",
    "name": "multiply_numbers",
    "description": "Multiply two numbers",
    "parameters": {
      "type": "object",
      "properties": {
        "a": { "type": "number", "description": "The first number" },
        "b": { "type": "number", "description": "The second number" }
      },
      "required": ["a", "b"],
      "additionalProperties": false
    }
  },
  {
    "type": "function",
    "name": "subtract_numbers",
    "description": "Subtract two numbers",
    "parameters": {
      "type": "object",
      "properties": {
        "a": { "type": "number", "description": "The first number" },
        "b": { "type": "number", "description": "The second number" }
      },
      "required": ["a", "b"],
      "additionalProperties": false
    }
  },
  {
    "type": "function",
    "name": "divide_numbers",
    "description": "Divide two numbers",
    "parameters": {
      "type": "object",
      "properties": {
        "a": { "type": "number", "description": "The numerator" },
        "b": { "type": "number", "description": "The denominator" }
      },
      "required": ["a", "b"],
      "additionalProperties": false
    }
  },
  {
    "type": "function",
    "name": "power",
    "description": "Raise a number to a power",
    "parameters": {
      "type": "object",
      "properties": {
        "base": { "type": "number", "description": "The base number" },
        "exponent": { "type": "number", "description": "The exponent" }
      },
      "required": ["base", "exponent"],
      "additionalProperties": false
    }
  },
  {
    "type": "function",
    "name": "square_root",
    "description": "Take the square root of a number",
    "parameters": {
      "type": "object",
      "properties": {
        "x": { "type": "number", "description": "The number to take the square root of" }
      },
      "required": ["x"],
      "additionalProperties": false
    }
  }
]
```
`src/core/tools/schemas/final_answer.json`
```json
{
  "type": "function",
  "name": "final_answer",
  "description": "Provide the final answer and stop.",
  "parameters": {
    "type": "object",
    "properties": {
      "answer": { "type": "string", "description": "The final answer for the user." }
    },
    "required": ["answer"],
    "additionalProperties": false
  }
}
```
`src/core/tools/functions/math.py`
```python
def sum_numbers(a: float, b: float) -> float:
    return a + b


def multiply_numbers(a: float, b: float) -> float:
    return a * b


def subtract_numbers(a: float, b: float) -> float:
    return a - b


def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


def power(base: float, exponent: float) -> float:
    return base ** exponent


def square_root(x: float) -> float:
    if x < 0:
        raise ValueError("Square root of negative number")
    return x ** 0.5
```
### Unit 2 - Taking Ownership of our Prompts
#### Goal
Extract system prompts and context formats to versioned markdown files, and use a serializer to control what the model sees (Factors 2 and 3).

#### Files
`src/core/prompts/base_system.md`
```markdown
# ROLE
You are an autonomous agent that can take multiple tool-calling steps.

# REQUIREMENTS
- If your work is done, call the final_answer tool
- ALWAYS prefer calling tools to compute, fetch, or transform information rather than fabricating results.

# EXTRA INSTRUCTIONS

```

`src/core/prompts/context_format.md`
```markdown
# User Request
{user_message}

# Actions Already Completed (DO NOT REPEAT)

{execution_history}

# Next Step
Decide what tool to call next to make progress on the request.
```

`src/core/utils/context_serializer.py`
```python
import json
from typing import List, Dict, Any
from pathlib import Path


_template_path = Path(__file__).resolve().parent.parent / "prompts" / "context_format.md"
_CONTEXT_TEMPLATE = _template_path.read_text(encoding="utf-8")


def serialize_context_to_text(context: List[Dict[str, Any]]) -> str:
    if not context:
        return ""

    user_message = ""
    for item in context:
        if item.get("role") == "user":
            user_message = item.get("content", "")
            break

    call_map = {}
    for item in context:
        if item.get("type") == "function_call":
            call_id = item.get("call_id")
            call_name = item.get("name")
            call_args = item.get("arguments", "{}")

            if isinstance(call_args, str):
                try:
                    call_args = json.loads(call_args)
                except:
                    pass

            if isinstance(call_args, dict):
                args_str = ", ".join(f"{k}={repr(v)}" for k, v in call_args.items())
            else:
                args_str = str(call_args)

            call_map[call_id] = f"{call_name}({args_str})"

    lines = []
    for item in context:
        if item.get("type") == "function_call_output":
            call_id = item.get("call_id")
            output = item.get("output", "{}")
            call_formatted = call_map.get(call_id, f"unknown_call({call_id})")
            lines.append(f"✓ COMPLETED: {call_formatted} → Result: {output}")

    execution_history = "\n".join(lines) if lines else "(No actions completed yet)"

    return _CONTEXT_TEMPLATE.format(
        user_message=user_message,
        execution_history=execution_history
    )
```
`src/core/agent.py`
```python
import json
import openai
from pathlib import Path
from typing import List, Any

from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)
from core.utils.context_serializer import serialize_context_to_text


class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps
        # Load system prompt from file (Factor 2).
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions

        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]

    def _call_llm(self, context: List[Any]):
        # Serialize context to control what the model sees (Factor 3).
        serialized_content = serialize_context_to_text(context)

        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=serialized_content,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _next_step(self, context: List[Any]):
        response = self._call_llm(context)
        function_calls = [item for item in response.output if item.type == "function_call"]

        for fc in function_calls:
            call_name = fc.name
            call_arguments = json.loads(fc.arguments)

            context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": fc.arguments,
                "call_id": fc.call_id
            })

            if call_name == "final_answer":
                return context, "complete", call_arguments.get("answer")

            match call_name:
                case "sum_numbers":
                    try:
                        result = sum_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "multiply_numbers":
                    try:
                        result = multiply_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "subtract_numbers":
                    try:
                        result = subtract_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "divide_numbers":
                    try:
                        result = divide_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "power":
                    try:
                        result = power(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "square_root":
                    try:
                        result = square_root(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case _:
                    output = json.dumps({"result": f"Error: Tool {call_name} not found"})

            context.append({
                "type": "function_call_output",
                "call_id": fc.call_id,
                "output": output
            })

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
        # Handle max steps case
        if status == "running":
            status = "max_steps_reached"

        # Return the final state
        return context, status, final_answer
```
`src/main.py`
```python
from core.agent import Agent

agent = Agent(max_steps=10)

context = [
    {
        "role": "user",
        "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
    }
]

context, status, final_answer = agent.run(context)

print(f"Status: {status}")
print(f"Final answer: {final_answer}")
print("\nFinal context:")
for item in context:
    print(item)
```
### Unit 3 - Unifying Execution and Business States
#### Goal
Create a unified State class that combines execution state (steps, status) with business state (context, final_answer), implementing Factor 5 (Unify execution state and business state).

#### Files
`src/core/models/state.py`
```python
from typing import List, Any, Optional
from pydantic import BaseModel, Field


class State(BaseModel):
    id: str
    steps: int = 0
    status: str = "running"
    context: List[Any] = Field(default_factory=list)
    pending_tool_calls: List[Any] = Field(default_factory=list)
    error: Optional[str] = None
    final_answer: Optional[str] = None
```
`src/core/agent.py`
```python
import json
import openai
from pathlib import Path
from typing import List, Any

from core.models.state import State
from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root
)
from core.utils.context_serializer import serialize_context_to_text


class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "",
        max_steps: int = 10
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_steps = max_steps

        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions

        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema
        ]

    def _call_llm(self, context: List[Any]):
        serialized_content = serialize_context_to_text(context)
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=serialized_content,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

    def _next_step(self, state: State):
        # State carries both execution and business data (Factor 5).
        state.steps += 1

        for function_call in list(state.pending_tool_calls):
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]
            call_id = function_call["call_id"]

            # Persist the tool call into unified context history.
            state.context.append({
                "type": "function_call",
                "name": call_name,
                "arguments": json.dumps(call_arguments),
                "call_id": call_id
            })

            match call_name:
                case "final_answer":
                    state.pending_tool_calls = []
                    state.status = "complete"
                    state.final_answer = call_arguments.get("answer")
                    return state
                case "sum_numbers":
                    try:
                        result = sum_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "multiply_numbers":
                    try:
                        result = multiply_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "subtract_numbers":
                    try:
                        result = subtract_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "divide_numbers":
                    try:
                        result = divide_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "power":
                    try:
                        result = power(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "square_root":
                    try:
                        result = square_root(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case _:
                    output = json.dumps({"result": f"Error: Tool {call_name} not found"})

            state.pending_tool_calls.remove(function_call)
            # Store tool output in the same state object.
            state.context.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            })

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

        # Queue new tool calls inside the unified state for the next step.
        state.pending_tool_calls.extend(function_call_dicts)
        return state

    def run(self, state: State):
        # Create a deep copy to avoid mutating the original
        state = state.model_copy(deep=True)

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

agent = Agent()

state = State(
    id=str(uuid.uuid4()),
    context=[
        {
            "role": "user",
            "content": "Solve the root of this equation: x^2 - 5x + 6 = 0"
        }
    ],
    status="running"
)

state = agent.run(state)

print(f"Status: {state.status}")
print(f"Final answer: {state.final_answer}")
```

---

# Course 4: Exposing Agents with Simple APIs in Python

## Overview
Expose agents as services reachable from any interface. With Factors 5, 6, 7, and 11, you’ll persist unified state in a database, orchestrate runs via background tasks and REST endpoints, and add pause/resume controls. Wire human responses back into waiting workflows and decouple triggers from UI so web apps, bots, and systems can launch, monitor, and resume runs at scale.


## Outline
### Unit 1 - Launching Agents with RESTful APIs
#### Goal
Build a FastAPI server with endpoints to launch agents and retrieve state, using in-memory storage and background tasks. By decoupling agent logic from any single interface and exposing it via REST APIs, this unit implements Factor 11 (Trigger from anywhere, meet users where they are).
#### Files
`src/server/main.py`
```python
import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict

from core.models.state import State
from core.agent import Agent

# Create agent
agent = Agent()

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
    json={"input_prompt": "Solve the root of this equation: x^2 - 5x + 6 = 0"}
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
#### Files
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
from typing import List, Any
from pathlib import Path

from core.models.state import State
from core.tools.functions.math import (
    sum_numbers,
    multiply_numbers,
    subtract_numbers,
    divide_numbers,
    power,
    square_root,
)
from core.utils.context_serializer import serialize_context_to_text

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        reasoning_effort: str = "low",
        extra_instructions: str = "None",
        max_steps: int = 10
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions
        self.max_steps = max_steps

        # Load tool schemas from JSON files.
        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"
        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)
        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)
        with open(schemas_dir / "ask_human.json", "r", encoding="utf-8") as f:
            ask_human_schema = json.load(f)

        self.tool_schemas = [
            *math_schemas,
            final_answer_schema,
            ask_human_schema,
        ]

    def _call_llm(self, context: List[Any]):
        # Serialize context to control what the model sees (Factor 3).
        serialized_content = serialize_context_to_text(context)

        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=serialized_content,
            tools=self.tool_schemas,
            tool_choice="required",
            reasoning={"effort": self.reasoning_effort} if self.model == "gpt-5" else None
        )
        return response

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

            if call_name == "ask_human":
                state.pending_tool_calls.remove(function_call)
                state.status = "waiting_human_input"
                return state

            if call_name == "final_answer":
                state.pending_tool_calls = []
                state.status = "complete"
                state.final_answer = call_arguments.get("answer") or None
                return state

            match call_name:
                case "sum_numbers":
                    try:
                        result = sum_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "multiply_numbers":
                    try:
                        result = multiply_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "subtract_numbers":
                    try:
                        result = subtract_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "divide_numbers":
                    try:
                        result = divide_numbers(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "power":
                    try:
                        result = power(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case "square_root":
                    try:
                        result = square_root(**call_arguments)
                        output = json.dumps({"result": result})
                    except Exception as e:
                        output = json.dumps({"result": f"Error: {str(e)}"})
                case _:
                    output = json.dumps({"result": f"Error: Tool {call_name} not found"})

            state.pending_tool_calls.remove(function_call)
            state.context.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            })

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

    def run(self, state: State, progress_callback=None):
        """
        Execute agent steps on a given state.
        The state should already be initialized with context and status.
        If state is paused/waiting, it will be set to running and execution will continue.
        
        Args:
            state: The state to run
            progress_callback: Optional callback(state) called after each step
        """
        # Keep run() non-mutating for callers by working on a deep copy.
        state = state.model_copy(deep=True)

        state.status = "running"

        is_resuming = state.steps > 0
        max_steps_allowed = (self.max_steps + state.steps) if is_resuming else self.max_steps

        while state.status == "running" and state.steps < max_steps_allowed:
            state = self._next_step(state)
            if progress_callback:
                progress_callback(state)

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
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

# Create agent
agent = Agent(max_steps=10)

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

#### Files
`src/server/main.py`
```python
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

agent = Agent()

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

        # If waiting for ask_human, require provide_input instead of resume
        if db_state.status == "waiting_human_input":
            raise HTTPException(status_code=400, detail="Agent is waiting for human input")

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
#### Files
`src/server/main.py`
```python
import json
import logging
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.models.state import State
from core.agent import Agent
from server.database import get_db_session, StateModel, pydantic_to_db, db_to_pydantic

logging.basicConfig(level=logging.INFO)

agent = Agent()

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

def _save_state_to_db(state_id: str, state: State):
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
    with get_db_session() as session:
        db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
        if db_state:
            db_state.status = "failed"
            db_state.error = error
            db_state.pending_tool_calls = []
            session.commit()

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
    try:
        if working_state is None:
            with get_db_session() as session:
                db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
                if not db_state:
                    return
                db_state.status = "running"
                db_state.error = None
                session.commit()
                working_state = db_to_pydantic(db_state)
        else:
            with get_db_session() as session:
                db_state = session.query(StateModel).filter(StateModel.id == state_id).first()
                if db_state:
                    db_state.status = "running"
                    db_state.error = None
                    session.commit()

        save_progress = _create_progress_callback(state_id)
        final_state = agent.run(working_state, progress_callback=save_progress)
        _save_state_to_db(state_id, final_state)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in background agent execution for {state_id}: {e}")
        _mark_state_failed(state_id, str(e))

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

        # If waiting for ask_human, require provide_input instead of resume
        if db_state.status == "waiting_human_input":
            raise HTTPException(status_code=400, detail="Agent is waiting for human input")

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
