import json
import requests
import time


class Client:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url

    def launch(self, input_prompt: str):
        """Launch a new agent and return the initial state"""
        url = f"{self.base_url}/agent/launch"
        payload = {
            "input_prompt": input_prompt
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def resume(self, state_id: str):
        """Resume a paused agent by its state ID"""
        url = f"{self.base_url}/agent/resume"
        payload = {
            "id": state_id
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_state(self, state_id: str):
        """Get the current state of an agent by its ID"""
        url = f"{self.base_url}/agent/state/{state_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = Client("http://localhost:3000")
    
    # Launch a new agent
    state = client.launch("Solve this equation: x^2 - 5x + 6 = 0")
    print("Launched agent:")
    print(json.dumps(state, indent=2))
    
    # Poll for updates until status is no longer "running"
    state_id = state["id"]
    print(f"\nPolling state {state_id}...")
    
    while True:
        current_state = client.get_state(state_id)
        status = current_state["status"]
        steps = current_state["steps"]
        print(f"Status: {status}, Steps: {steps}")
        
        if status != "running":
            final_state = current_state
            break
        
        time.sleep(3)  # Wait 3 seconds before polling again
    
    print("\nFinal state:")
    print(json.dumps(final_state, indent=2))


