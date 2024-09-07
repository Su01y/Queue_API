import functools
import logging

from psycopg2 import pool, OperationalError

from models import Config, Task


class Repository:
    """
    Repository class for managing database connections and executing SQL queries related to task management.

    This class uses a connection pool to interact with a PostgreSQL database and provides methods for creating tables and
    inserting task records. It manages the connections using psycopg2's SimpleConnectionPool and ensures safe database
    interactions via a custom decorator.

    Attributes:
    - cfg (Config): The configuration object containing the PostgreSQL connection details (user, host, password, database, port).
    - loop (EventLoop): The event loop to handle asynchronous operations.
    - connection_try (int): A counter that tracks connection attempts to the database.
    - conn_pool (SimpleConnectionPool): The connection pool for managing database connections.
    """
    def __init__(self, cfg: Config, loop):
        self.cfg = cfg
        self.loop = loop
        self.connection_try = 0
        self.conn_pool = None

    def init_pool(self):
        """
        Initializes a PostgreSQL connection pool using the parameters from the configuration object (cfg).

        The pool allows efficient database connection management by reusing connections, with a maximum of 5 and a minimum of 1.
        """
        try:
            self.conn_pool = pool.SimpleConnectionPool(user=self.cfg.pg.user,
                                                       host=self.cfg.pg.host,
                                                       password=self.cfg.pg.passwd,
                                                       database=self.cfg.pg.database,
                                                       port=self.cfg.pg.port,
                                                       maxconn=5,
                                                       minconn=1)
            logging.info(f"[Repository:init_pool] - successfully created pool")
        except OperationalError as e:
            logging.info(f"[Repository:init_pool] - error = {e}")

    def sql_query(func):
        """
        A decorator that manages database connections and executes the provided function (SQL query).

        Ensures:
        - A database connection is obtained from the pool before the query execution.
        - Commits the transaction and releases the connection back to the pool after execution.

        Parameters:
        - func (function): The function to be executed, which represents an SQL query.

        Returns:
        - The result of the wrapped function (SQL query), if successful.
        """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.conn_pool:
                self.init_pool()
            connection_db = self.conn_pool.getconn()
            cursor = connection_db.cursor()
            try:
                result = func(self, cursor, *args, **kwargs)
                if result:
                    return result
            except Exception as e:
                logging.info(f"[Repository:sql_query] - {str(func)} error {e}")
            finally:
                logging.info(f"[Repository:sql_query] - {str(func)} Connection closed")
                if connection_db:
                    connection_db.commit()
                    if cursor:
                        cursor.close()
                    self.conn_pool.putconn(connection_db)

        return wrapper

    @sql_query
    def create_table(self, cursor):
        query = """
            CREATE TABLE tasks (
                id SERIAL PRIMARY KEY,
                create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                start_time TIMESTAMP,
                exec_time INTERVAL
            );
        """
        cursor.execute(query)
        logging.info(f"[Repository:create_table] - The table was created")
        
    @sql_query
    def write_task(self, cursor, task: Task):
        query = """
                INSERT INTO tasks (id, create_time, start_time, exec_time) 
                VALUES (%s, %s, %s, %s);
            """
        task_data = (
            task.task_id,
            task.create_time,
            task.start_time,
            task.exec_time
        )
        cursor.execute(query, task_data)
        logging.info(f"[Repository:write_task] - write row")
