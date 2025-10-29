import json
import requests

from core.models.state import State


class Client:
    def __init__(self, url: str):
        self.url = url

    def send_request(self, payload: dict):
        response = requests.post(self.url, json=payload)
        return response.json()

    def launch(self, input_prompt: str):
        payload = {
            "input_prompt": input_prompt
        }
        return self.send_request(payload)

    def resume(self, state: State):
        payload = {
            "state": state
        }
        return self.send_request(payload)


if __name__ == "__main__":
    client = Client("http://localhost:3000/agent/launch")
    response = client.launch("Solve this equation: x^2 - 5x + 6 = 0")
    print(json.dumps(response, indent=2))


