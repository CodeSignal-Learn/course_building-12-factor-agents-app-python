from typing import List, Any, Optional
from pydantic import BaseModel, Field


class State(BaseModel):
    id: str
    steps: int = 0
    status: str = "running"
    context: List[Any] = Field(default_factory=list)
    pending_tool_calls: List[Any] = Field(default_factory=list)
    error: Optional[str] = None
    final_answer: Optional[str] = None