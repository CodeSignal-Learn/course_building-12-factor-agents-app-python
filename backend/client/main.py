import json
import requests
import time
from typing import Optional, Dict, Any

from core.tools.human_interaction import ask_human_cli


class Client:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def launch(self, input_prompt: str) -> Dict[str, Any]:
        """Launch a new agent and return the initial state"""
        url = f"{self.base_url}/agent/launch"
        response = requests.post(url, json={"input_prompt": input_prompt})
        response.raise_for_status()
        return response.json()

    def resume(self, state_id: str) -> Dict[str, Any]:
        """Resume a paused agent by its state ID"""
        url = f"{self.base_url}/agent/resume"
        response = requests.post(url, json={"id": state_id})
        response.raise_for_status()
        return response.json()

    def get_state(self, state_id: str) -> Dict[str, Any]:
        """Get the current state of an agent by its ID"""
        url = f"{self.base_url}/agent/state/{state_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def provide_input(self, state_id: str, answer: str) -> Dict[str, Any]:
        """Provide human input to a state waiting for human input"""
        url = f"{self.base_url}/agent/provide_input"
        response = requests.post(url, json={"id": state_id, "answer": answer})
        response.raise_for_status()
        return response.json()

    def extract_ask_human_call_from_state(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract the ask_human function call from state context"""
        context = state.get("context", [])
        for item in reversed(context):
            if (isinstance(item, dict) and 
                item.get("type") == "function_call" and 
                item.get("name") == "ask_human"):
                return item
        return None


def is_terminal_status(status: str) -> bool:
    """Check if a status indicates the agent has finished"""
    return status in ("complete", "failed", "max_steps_reached")


def handle_human_input(client: Client, state_id: str, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle waiting for human input using ask_human_cli. Returns updated state or None on error"""
    function_call_item = client.extract_ask_human_call_from_state(current_state)
    if not function_call_item:
        print("Agent is waiting for input but ask_human call not found")
        return current_state
    
    # Convert to format expected by ask_human_cli (arguments already JSON string from context)
    function_call_for_cli = {
        "arguments": function_call_item.get("arguments"),  # Already a JSON string
        "call_id": function_call_item.get("call_id")
    }
    
    try:
        # Use ask_human_cli to prompt user and get response
        response = ask_human_cli(function_call_for_cli)
        
        # Extract answer from the response
        output_data = json.loads(response["output"])
        answer = output_data.get("answer")
        
        # Submit answer to server
        updated_state = client.provide_input(state_id, answer)
        return updated_state
    except EOFError as e:
        print(f"Cannot request input in non-interactive environment: {e}")
        return current_state
    except requests.exceptions.HTTPError as e:
        print(f"Error providing input: {e}")
        return current_state  # Return last known state on error


def poll_until_complete(client: Client, state_id: str, poll_interval: float = 5.0) -> Optional[Dict[str, Any]]:
    """Poll agent state until it reaches a terminal status"""
    print(f"\nPolling state {state_id}...")
    
    while True:
        try:
            current_state = client.get_state(state_id)
            status = current_state["status"]
            steps = current_state["steps"]
            print(f"Status: {status}, Steps: {steps}")
            
            # Handle human input
            if status == "waiting_human_input":
                updated_state = handle_human_input(client, state_id, current_state)
                if updated_state:
                    current_state = updated_state
                    status = current_state["status"]
                time.sleep(poll_interval)
                continue
            
            # Check for terminal states
            if is_terminal_status(status):
                if status == "failed":
                    error = current_state.get("error", "Unknown error")
                    print(f"Agent failed: {error}")
                return current_state
            
            # Still running, continue polling
            time.sleep(poll_interval)
            
        except requests.exceptions.HTTPError as e:
            print(f"Error polling state: {e}")
            return None


def main():
    """Main entry point for the client"""
    client = Client("http://localhost:8000")
    
    # Launch a new agent
    prompt = "Solve the roots of this equation: x^2 - 5x + 6 = "
    state = client.launch(prompt)
    print("Launched agent:")
    print(json.dumps(state, indent=2))
    
    # Poll until completion
    final_state = poll_until_complete(client, state["id"])
    
    # Display results
    if final_state:
        print("\nFinal state:")
        print(json.dumps(final_state, indent=2))
    else:
        print("\nNo final state available (error occurred)")


if __name__ == "__main__":
    main()
