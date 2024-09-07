import logging
import time
import random
import threading
from collections import deque
from datetime import datetime

from repository import Repository
from models import TaskStatus, TaskInfo, Task


class TaskQueue:
    """
    Class that manages a queue of tasks with a limit on the number of tasks executed simultaneously.

    Attributes:
    - queue (deque): The task queue.
    - tasks (dict): Dict with all tasks
    - db (Repository): repository to save tasks
    - lock (threading.Lock): Lock for synchronizing access to task counters.
    - max_running_tasks (int): Maximum number of tasks that can run simultaneously.
    - running_tasks (int): Current number of tasks being executed.
    - task_id_counter (int): Counter for generating unique task IDs.
    - task_lock (threading.Lock): Lock for synchronizing access to the task queue.
    - condition (threading.Condition): Condition variable for controlling the worker thread.
    - worker_thread (threading.Thread): Background thread that processes tasks from the queue.
    """
    def __init__(self, db: Repository):
        self.queue = deque()
        self.tasks = {}
        self.db = db
        self.lock = threading.Lock()
        self.max_running_tasks = 2
        self.running_tasks = 0
        self.task_id_counter = 1
        self.task_lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def add_task(self) -> int:
        """
        Adds a new task to the queue and notifies the worker thread.

        Returns:
        - int: Unique identifier of the created task.
        """
        with self.task_lock:
            task_id = self.task_id_counter
            self.task_id_counter += 1
            logging.info(f"[TaskQueue:add_task] task {task_id} added in queue. Queue len = {len(self.queue)}")

            task = Task(task_id)
            self.tasks.update({task_id: task})
            self.queue.append(task)

        with self.condition:
            self.condition.notify()

        return task_id

    def _worker(self):
        """
        Worker thread that continuously checks the task queue and executes tasks as they become available.

        Executes tasks while respecting the limit on the number of simultaneously running tasks.
        """
        while True:
            with self.condition:
                while not self.queue or self.running_tasks >= self.max_running_tasks:
                    self.condition.wait()

                task = self.queue.popleft()
                task.status = TaskStatus.RUN
                task.start_time = datetime.now()
                logging.info(f"[TaskQueue:add_task] {task.task_id} started")
                self.running_tasks += 1

            time.sleep(random.randint(0, 10))

            with self.lock:
                task.status = TaskStatus.COMPLETED
                time_delta = datetime.now() - task.start_time
                task.exec_time = time_delta.total_seconds()
                self.db.write_task(task=task)
                logging.info(f"[TaskQueue:add_task] {task.task_id} stopped after {task.exec_time}")
                self.running_tasks -= 1

    def get_task_status(self, task_id: int) -> TaskInfo:
        with self.task_lock:
            task = self.tasks.get(task_id)
            if task:
                return TaskInfo(
                    status=task.status,
                    create_time=task.create_time,
                    start_time=task.start_time,
                    time_to_execute=task.exec_time
                )
            logging.info(f"[TaskQueue:get_task_status] {task_id} was not found")
