from datetime import datetime
from enum import Enum, auto
from typing import Optional

from pydantic import BaseModel
from pydantic_yaml import YamlModel


class PG(BaseModel):
    host: str
    database: str
    user: str
    passwd: str
    port: int


class Config(YamlModel):
    pg: PG


class TaskStatus(Enum):
    IN_QUEUE = "IN_QUEUE"
    RUN = "RUN"
    COMPLETED = "COMPLETED"


class TaskInfo(BaseModel):
    """
    Pydantic model to represent detailed information of a task.

    Attributes:
    - status (str): The current status of the task (e.g., 'IN_QUEUE', 'RUN', 'COMPLETED').
    - create_time (datetime): The time when the task was created.
    - start_time (Optional[datetime]): The time when the task started execution, or None if not started yet.
    - time_to_execute (Optional[int]): The time taken for task execution in seconds, or None if not yet completed.
    """
    status: TaskStatus
    create_time: datetime
    start_time: Optional[datetime] = None
    time_to_execute: Optional[int] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class Task:
    """
    Class representing a task in the queue.

    Attributes:
    - task_id (int): Unique task identifier.
    - status (TaskStatus): Current status of the task.
    - create_time (datetime): Time when the task was created.
    - start_time (Optional[datetime]): Time when the task started running.
    - exec_time (Optional[int]): Time taken for task execution (in seconds).
    """
    def __init__(self, task_id):
        self.task_id = task_id
        self.status = TaskStatus.IN_QUEUE
        self.create_time = datetime.now()
        self.start_time: Optional[datetime] = None
        self.exec_time: Optional[float] = None
