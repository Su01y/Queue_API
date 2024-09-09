import logging
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from repository import Repository
from models import TaskStatus, TaskInfo, Task


class TaskQueue:
    """
    TaskQueue manages the execution of tasks using a queue system, ensuring that at most
    two tasks run concurrently. It automatically picks tasks from the queue and executes
    them as workers become available.

    Attributes:
        tasks (dict): Stores task objects by their unique task ID.
        queue (list): Holds the task IDs in the order they were added.
        db (Repository): Repository to save tasks.
        lock (Lock): Ensures thread-safe access to shared resources.
        executor (ThreadPoolExecutor): A thread pool that runs tasks, limited to 2 concurrent workers.
        task_id_counter (int): Counter for generating unique task IDs.
    """
    def __init__(self, db: Repository):
        self.tasks = {}
        self.queue = []
        self.db = db
        self.lock = threading.Lock()
        self.task_id_counter = 1
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.active_futures = set()

    def add_task(self):
        """
        Adds a new task to the queue and returns its unique task ID.

        Returns:
            int: The unique task ID of the added task.
        """
        with self.lock:
            task_id = self.task_id_counter
            self.task_id_counter += 1
            task = Task(task_id)
            self.tasks[task_id] = task
            self.queue.append(task_id)
        return task_id

    def _run_task(self, task):
        """
        Simulates running a task by sleeping for a random amount of time between 1 and 10 seconds.
        Updates the task's status once complete.

        Args:
            task (Task): The task object to be executed.
        """
        task.exec_time = random.randint(1, 10)
        task.start_time = datetime.now()
        time.sleep(task.exec_time)
        with self.lock:
            task.status = TaskStatus.COMPLETED
            task.end_time = time.time()
            time_delta = datetime.now() - task.start_time
            task.exec_time = time_delta.total_seconds()
            self.db.write_task(task=task)
        logging.info(f"[TaskQueue:add_task] {task.task_id} stopped after {task.exec_time}")

    def _task_cleanup(self, future, task_id):
        """
        Callback function to be executed once the task is completed.
        It removes the completed task from the active futures set.

        Args:
            future (concurrent.futures.Future): The future representing the task.
        """
        with self.lock:
            self.active_futures.remove(future)

    def start_processing(self):
        """
        Starts a continuous process that monitors the task queue and submits tasks to the executor
        as long as there are tasks in the queue and fewer than two tasks running.
        """
        while True:
            with self.lock:
                while len(self.active_futures) < 2 and self.queue:
                    task_id = self.queue.pop(0)
                    task = self.tasks[task_id]
                    task.status = TaskStatus.RUN
                    logging.info(f"[TaskQueue:start_processing] {task.task_id} started")

                    future = self.executor.submit(self._run_task, task)
                    future.add_done_callback(lambda f: self._task_cleanup(f, task_id))
                    self.active_futures.add(future)
            time.sleep(1)


    def start_background_worker(self):
        """
        Starts a background thread that runs the task processing loop continuously.
        """
        worker_thread = threading.Thread(target=self.start_processing)
        worker_thread.daemon = True
        worker_thread.start()

    def get_task_status(self, task_id: int) -> TaskInfo:
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                return TaskInfo(
                    status=task.status,
                    create_time=task.create_time,
                    start_time=task.start_time,
                    time_to_execute=task.exec_time
                )
            logging.info(f"[TaskQueue:get_task_status] {task_id} was not found")
