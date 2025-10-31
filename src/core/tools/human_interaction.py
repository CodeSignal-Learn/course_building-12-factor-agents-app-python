import json

def ask_human_cli(function_call: dict) -> dict:
    """
    Ask the user for clarification or additional information.
    
    Args:
        function_call (dict): The function call to ask the user
        
    Returns:
        dict: The function call output
        
    Raises:
        EOFError: If input is not available (non-interactive environment)
    """
    # Parse arguments from JSON string
    arguments = json.loads(function_call['arguments'])
    
    try:
        # Ask the user for clarification
        response = input(f"\nAgent is asking: {arguments['question']}\n> ")
        # Return the function call output
        return {
            "type": "function_call_output",
            "call_id": function_call["call_id"],
            "output": json.dumps({
                "answer": response
            })
        }
    except EOFError:
        raise EOFError("Cannot request clarification in non-interactive environment")
