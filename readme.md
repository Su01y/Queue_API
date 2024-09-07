# Task Queue API
This project implements a simple task queue system using PostgreSQL for task storage and management. It includes an API for creating tasks, checking task statuses, and managing task execution.

## Features
* Task management using a PostgreSQL database.
* Connection pooling to efficiently manage database connections.
* Task queue with status tracking (In Queue, Run, Completed).
* API endpoints to create tasks and check their status.
* Concurrency control with task processing limited to two simultaneous executions.
## Prerequisites
Before you start, make sure you have the following installed:

* Python 3.9
* PostgreSQL
* pip for Python package management
## Getting Started
1. ### Clone the repository:
```bash
git clone https://github.com/your-username/task-queue-api.git
cd task-queue-api
```
2. ### Create a configuration file:
Create a `config.yaml` file in the project root directory to store the database credentials:

```yaml
pg:
  host: host
  database: database
  user: user
  passwd: password
  port: port
```

## Installation
1. ### Install dependencies:
```bash
pip install -r requirements.txt
```
2. ### Set up the database:
Once the dependencies are installed, run the project to set up the database tables. The `Repository` class will handle creating the necessary tables.

3. ### Run the server:

Start the API server:

```bash
python3.9 app.py
```
This will start the server on http://localhost:8000.

## API Documentation
1. ### Create a Task
__Endpoint__: `/task/create`

* __Method__: GET
* __Description__: Creates a new task and adds it to the queue.
* __Response__: Returns the task ID.
```bash
curl -X GET http://localhost:8000/task/create
```
__Response__:

```json
{
    "task_id": 1
}
```
2. ### Get Task Status
__Endpoint__: `/task/status/{task_id}`

* __Method__: GET
* __Description__: Retrieves the status of the specified task.
* __Response__: Returns the task status, creation time, start time, and execution duration (if completed).
```bash
curl -X GET http://localhost:8000/task/status/1
```
__Response__:

```json
{
    "status": "Run",
    "create_time": "2024-09-07 10:05:00",
    "start_time": "2024-09-07 10:06:00",
    "time_to_execute": 4
}
```
3. ### Available Task Statuses
* __In Queue__: Task is waiting to be processed.
* __Run__: Task is currently being executed.
* __Completed__: Task has been successfully completed.
## Project Structure
```bash
task-queue-api/
│
├── app.py                   # Entry point for running the API
├── models.py                # Data models (Task, Config)
├── my_queue.py              # Queue management logic
├── repository.py            # Repository class for DB interactions
├── service.py               # Service class for manage api
├── config.yaml              # Configuration file for database credentials
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation (this file)
```
