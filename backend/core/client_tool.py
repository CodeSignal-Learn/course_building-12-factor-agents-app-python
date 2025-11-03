import inspect
import json
from typing import get_origin, get_type_hints


class ClientTool:
    def __init__(self, name: str, description: str, function, require_approval: bool = False):
        self.name = name
        self.description = description
        self.function = function
        self.require_approval = require_approval
        self.schema = self._generate_schema()

    def execute(self, **kwargs):
        if self.require_approval:
            try:
                approved = input(
                    f"Approve '{self.name}' with args:\n{json.dumps(kwargs, indent=2)}\n[y/N]: "
                ).strip().lower() in ("y", "yes")
            except EOFError:
                approved = False
            if not approved:
                raise PermissionError("Execution not approved by user")
        return self.function(**kwargs)

    def _generate_schema(self):
        signature = inspect.signature(self.function)
        annotations = get_type_hints(self.function)
        type_map = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
            tuple: "array",
            type(None): "null",
        }
        properties = {}
        required = []
        for param_name, param in signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            annotation = annotations.get(param_name, str)
            origin = get_origin(annotation)
            base = origin or annotation
            json_type = type_map.get(base, "string")
            properties[param_name] = {"type": json_type}
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        }


