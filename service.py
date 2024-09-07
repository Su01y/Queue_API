from models import TaskInfo
from repository import Repository
from my_queue import TaskQueue


class TaskManager:
    """
    Class to manage API endpoints for task creation and status checking.

    Attributes:
    - task_queue (TaskQueue): Instance of TaskQueue to manage task processing.
    """
    def __init__(self, db: Repository):
        self.task_queue = TaskQueue(db=db)

    def create_task(self) -> dict:
        task_id = self.task_queue.add_task()
        return {"task_id": task_id}

    def get_task_status(self, task_id: int) -> TaskInfo:
        task_info = self.task_queue.get_task_status(task_id)
        if task_info:
            return task_info
