from typing import List, Any, Optional
from pydantic import BaseModel


class State(BaseModel):
    id: str
    steps: int = 0
    status: str = "running"
    context: List[Any] = []
    pending_tool_calls: List[Any] = []
    error: Optional[str] = None
    final_answer: Optional[str] = None