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

        # Load tool schemas from JSON files
        schemas_dir = Path(__file__).resolve().parent / "tools" / "schemas"

        with open(schemas_dir / "math.json", "r", encoding="utf-8") as f:
            math_schemas = json.load(f)

        with open(schemas_dir / "final_answer.json", "r", encoding="utf-8") as f:
            final_answer_schema = json.load(f)

        with open(schemas_dir / "ask_human.json", "r", encoding="utf-8") as f:
            ask_human_schema = json.load(f)

        # Prepare tool schemas for the LLM
        self.tool_schemas = [
            *math_schemas,
            final_answer_schema,
            ask_human_schema
        ]

    def _call_llm(self, context: List[Any]):
        # Serialize the entire context history into a single user message
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
        # Increment step
        state.steps = state.steps + 1

        # Iterate over a copy to allow safe removal during iteration
        for function_call in list(state.pending_tool_calls):
            # Get the call name, arguments and id
            call_name = function_call["name"]
            call_arguments = function_call["arguments"]
            call_id = function_call["call_id"]

            # Add the tool call to state.context (serialize arguments to JSON for storage)
            state.context.append(
                {
                    "type": "function_call",
                    "name": call_name,
                    "arguments": json.dumps(call_arguments),  # Serialize dict to JSON string
                    "call_id": call_id,
                }
            )

            # Execute tool using match/case
            match call_name:
                case "ask_human":
                    # Remove this tool call from state.pending_tool_calls
                    state.pending_tool_calls.remove(function_call)
                    # Set state.status to waiting_human_input
                    state.status = "waiting_human_input"
                    # Return state
                    return state

                case "final_answer":
                    # Set state.pending_tool_calls to empty list
                    state.pending_tool_calls = []
                    # Set state.status to complete
                    state.status = "complete"
                    # Persist the final answer on the state
                    state.final_answer = call_arguments.get("answer") or None
                    # Return state
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

            # For regular tools (not ask_human or final_answer), add result to context
            if call_name not in ["ask_human", "final_answer"]:
                # Remove this tool call from state.pending_tool_calls
                state.pending_tool_calls.remove(function_call)
                # Add the tool result to state.context
                state.context.append({
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": output
                })

        # Call LLM
        response = self._call_llm(state.context)

        # Find all tool calls and convert to dicts for JSON serialization
        function_calls = [item for item in response.output if item.type == "function_call"]
        
        # Convert SDK objects to plain dicts for storage
        function_call_dicts = [
            {
                "name": fc.name,
                "arguments": json.loads(fc.arguments),  # Parse once, store as dict
                "call_id": fc.call_id,
                "type": fc.type,
            }
            for fc in function_calls
        ]

        # Add new tool calls to state.pending_tool_calls
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
        state = state.model_copy(deep=True)

        # Ensure state is set to running
        state.status = "running"
        
        # Calculate max steps: if resuming (steps > 0), allow continuing from current step count
        is_resuming = state.steps > 0
        max_steps_allowed = (self.max_steps + state.steps) if is_resuming else self.max_steps

        # Call next step until complete or waiting_human_input
        while state.status == "running" and state.steps < max_steps_allowed:
            state = self._next_step(state)
            # Call progress callback if provided
            if progress_callback:
                progress_callback(state)

        # If still running and max steps reached, set status to max_steps_reached
        if state.status == "running" and state.steps >= max_steps_allowed:
            state.status = "max_steps_reached"
        
        return state
