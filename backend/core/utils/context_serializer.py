import json
from typing import List, Dict, Any
from pathlib import Path


# Load the context format template
_template_path = Path(__file__).resolve().parent.parent / "prompts" / "context_format.md"
_CONTEXT_TEMPLATE = _template_path.read_text(encoding="utf-8")


def serialize_context_to_text(context: List[Dict[str, Any]]) -> str:
    """
    Serialize structured context into a formatted text message using a template.

    The template is loaded from core/prompts/context_format.md and filled with:
    - {user_message}: The initial user request
    - {execution_history}: Formatted list of completed tool calls and results

    Args:
        context: List of context items (user messages, function calls, function outputs)

    Returns:
        Formatted string ready to send to LLM
    """
    if not context:
        return ""

    # Extract initial user message
    user_message = ""
    for item in context:
        if item.get("role") == "user":
            user_message = item.get("content", "")
            break

    # Build a map of call_id -> formatted call string
    call_map = {}
    for item in context:
        if item.get("type") == "function_call":
            call_id = item.get("call_id")
            call_name = item.get("name")
            call_args = item.get("arguments", "{}")

            # Parse arguments if string
            if isinstance(call_args, str):
                try:
                    call_args = json.loads(call_args)
                except:
                    pass

            # Format arguments as key=value pairs
            if isinstance(call_args, dict):
                args_str = ", ".join(f"{k}={repr(v)}" for k, v in call_args.items())
            else:
                args_str = str(call_args)

            call_map[call_id] = f"{call_name}({args_str})"

    # Build execution history by pairing calls with their outputs
    lines = []
    for item in context:
        if item.get("type") == "function_call_output":
            call_id = item.get("call_id")
            output = item.get("output", "{}")

            # Look up the matching call and format together
            call_formatted = call_map.get(call_id, f"unknown_call({call_id})")
            lines.append(f"✓ COMPLETED: {call_formatted} → Result: {output}")

    # Format execution history
    execution_history = "\n".join(lines) if lines else "(No actions completed yet)"

    # Fill in the template
    result = _CONTEXT_TEMPLATE.format(
        user_message=user_message,
        execution_history=execution_history
    )

    return result
