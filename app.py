import logging
import os

from fastapi import FastAPI, HTTPException
import asyncio
import uvicorn

from service import TaskManager
from models import Config, TaskInfo
from repository import Repository


app = FastAPI()

logging.basicConfig(level=logging.INFO)
cfg = Config.parse_file(os.path.dirname(__file__) + '/config.yaml')
loop = asyncio.get_event_loop()
db = Repository(cfg=cfg, loop=loop)
task_manager = TaskManager(db=db)


@app.on_event("startup")
async def startup_event():
    db.init_pool()
    db.create_table()


@app.get("/task/create")
def create_task():
    """
    API endpoint to create a task and return its task ID.
    """
    return task_manager.create_task()


@app.get("/task/status/{task_id}", response_model=TaskInfo)
def get_task_status(task_id: int):
    """
    API endpoint to return the status of a task by its ID.

    Parameters:
    - task_id (int): The task ID to retrieve the status for.

    Returns:
    - TaskInfo: A JSON object containing the task's status, creation time, start time, and execution time.
    """
    task_info = task_manager.get_task_status(task_id=task_id)
    if task_info:
        return task_info
    raise HTTPException(status_code=404, detail="Task not found")


if __name__ == '__main__':
    uvicorn.run(app=app)
