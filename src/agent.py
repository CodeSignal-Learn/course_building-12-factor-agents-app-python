import json
import uuid
import openai
from typing import List, Any
from models.state import State
from client_tool import ClientTool

class Agent:
    def __init__(
        self,
        model: str = "gpt-5",
        extra_instructions: str = "None",
        max_steps: int = 10,
        tools: List[ClientTool] = []
    ):
        self.model = model
        self.system_prompt = open(f"prompts/base_system.md").read() + extra_instructions
        self.max_steps = max_steps
        # Map tools by name for quick lookup and prepare tool schemas for the LLM
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

    def _call_llm(self, context: List[Any]):
        response = openai.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=context,
            tools=self.tool_schemas
        )
        return response

    def _call_tool(self, function_call):
        # Get tool name, id and input
        tool_name = function_call.name
        call_id = function_call.call_id
        tool_input = json.loads(function_call.arguments)

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

        # Call LLM
        response = self._call_llm(state.context)

        # Find all tool calls and assign to state.pending_tool_calls
        state.pending_tool_calls = [item for item in response.output if item.type == "function_call"]

        # Iterate over all pending tool calls
        for function_call in state.pending_tool_calls:
            # Parse the arguments
            parsed_args = json.loads(function_call.arguments)

            # Add the tool call to state.context
            state.context.append(
                {
                    "type": "function_call",
                    "name": function_call.name,
                    "arguments": function_call.arguments,
                    "call_id": function_call.call_id,
                }
            )

            # If called ask_human tool
            if function_call.name == "ask_human":
                # Remove this tool call from state.pending_tool_calls
                state.pending_tool_calls.remove(function_call)
                # Set state.status to paused
                state.status = "paused"
                # Return state
                return state

            # If called final_answer tool
            if function_call.name == "final_answer":
                # Set state.pending_tool_calls to empty list
                state.pending_tool_calls = []
                # Set state.status to complete
                state.status = "complete"
                # Persist the final answer on the state
                state.final_answer = parsed_args.get("answer") or None
                # Return state
                return state

            # Call the regular tool 
            result = self._call_tool(function_call)
            # Remove this tool call from state.pending_tool_calls
            state.pending_tool_calls.remove(function_call)
            # Add the tool result to state.context
            state.context.append(result)

        return state
                
    def run(self, input: str):     
        context = [
            {"role": "user", "content": input},
        ]

        state = State(id=str(uuid.uuid4()), context=context)

        # Call next step until complete or paused
        while state.status == "running" and state.steps < self.max_steps:
            state = self._next_step(state)

        # If max steps reached, set status to max_steps_reached
        if state.steps == self.max_steps:
            state.status = "max_steps_reached"
        
        return state

    def resume(self, state: State):
        # Set status to running
        state.status = "running"

        # Call next step until complete or paused
        while state.status == "running" and state.steps < (self.max_steps + state.steps):
            state = self._next_step(state)
        
        # If max steps reached, set status to max_steps_reached
        if state.steps == self.max_steps:
            state.status = "max_steps_reached"

        # Return state
        return state