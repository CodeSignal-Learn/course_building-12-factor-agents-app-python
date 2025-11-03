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
        prompt_path = Path(__file__).resolve().parent / "prompts" / "base_system.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") + extra_instructions
        self.max_steps = max_steps
        # Map tools by name for quick lookup and prepare tool schemas for the LLM
        tools = tools or []
        self.tools = {tool.name: tool for tool in tools}
        self.tool_schemas = [tool.schema for tool in tools]
        # Built-in tool: final_answer
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
        # Built-in tool: ask_human
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

    def _call_tool(self, function_call):
        # Get tool name, id and input (handle both dict and object)
        tool_name = function_call["name"]
        call_id = function_call["call_id"]
        tool_input = function_call["arguments"]


        # Execute tool and handle errors
        try:
            result = self.tools[tool_name].execute(**tool_input)
        except KeyError:
            result = f"Error: Tool {tool_name} not found"
        except Exception as e:
            result = f"Error: {str(e)}"
        return {"type": "function_call_output", "call_id": call_id, "output": json.dumps({"result": result})}

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

            # If called ask_human tool
            if call_name == "ask_human":
                # Remove this tool call from state.pending_tool_calls
                state.pending_tool_calls.remove(function_call)
                # Set state.status to waiting_human_input
                state.status = "waiting_human_input"
                # Return state
                return state

            # If called final_answer tool
            if call_name == "final_answer":
                # Set state.pending_tool_calls to empty list
                state.pending_tool_calls = []
                # Set state.status to complete
                state.status = "complete"
                # Persist the final answer on the state
                state.final_answer = call_arguments.get("answer") or None
                # Return state
                return state

            # Call the regular tool (convert to dict format)
            tool_call_dict = {
                "name": call_name,
                "arguments": call_arguments,
                "call_id": call_id
            }
            result = self._call_tool(tool_call_dict)
            # Remove this tool call from state.pending_tool_calls
            state.pending_tool_calls.remove(function_call)
            # Add the tool result to state.context
            state.context.append(result)

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