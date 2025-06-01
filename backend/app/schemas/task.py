from typing import Any

from pydantic import BaseModel

class TaskResponse(BaseModel):
    task_id: str
    status: str      # PENDING, STARTED, SUCCESS, FAILURE

class TaskStatus(TaskResponse):
    task_id: str
    status: str
    result: Any | None = None