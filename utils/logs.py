import time
import logging
from typing import Any
from pathlib import Path
from functools import wraps

from utils.paths import getFileSystemPath
from utils.envHandler import getenv

APP_BASE_PATH = getenv('APP_BASE_PATH')

class Logger(object):
    """
    A class to handle logging functionality with support for console and file handlers.

    Attributes:
    ----------
    name (str): The name of the logger.
    logger (logging.Logger): The actual logger object.
    formatter (logging.Formatter): The formatter for log messages.

    Methods:
    -------
    __init__(self, name: str = None): Initializes the logger with the given name.
    _add_console_handler(self): Adds a console handler to the logger.
    _add_file_handler(self): Adds a file handler to the logger.
    get_logger(self) -> logging.Logger: Returns the logger object.
    log(self, level: str, message: str, error: Any = None, params: Any = None): Logs a message with the given level, error, and params.
    """
    def __init__(self, name: str = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Ensure handlers are not duplicated
        if not self.logger.hasHandlers():
            self._add_console_handler()
            self._add_file_handler()

    def _add_console_handler(self):
        """Adds a console handler to the logger."""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """Adds a file handler to the logger."""
        base_path = getFileSystemPath(base_directory=APP_BASE_PATH)
        log_dir = Path(base_path, 'logs')
        log_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        log_file_path = log_dir / f"{self.name}.log"
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """Returns the logger object."""
        return self.logger
    
    def log(self, level: str, message: str, error: Any = None, params: Any = None):
        """
        Logs a message with the given level, error, and params.

        Parameters:
        level (str): The log level (e.g., 'info', 'warning', 'error').
        message (str): The main log message.
        error (Any, optional): The error associated with the log message. Defaults to None.
        params (Any, optional): Additional parameters related to the log message. Defaults to None.

        Returns:
        None
        """
        if error:
            message = f"{message} | Error: {error}"
        if params:
            message = f"{message} | Params: {params}"

        log_method = getattr(self.logger, level.lower(), None)
        if callable(log_method):
            log_method(f"{message}\n\n")
        else:
            self.logger.error(f"Invalid log level: {level}. Message: {message}")

# Define the timer decorator that accepts a logger
def timer(logger=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()  # Record the start time
            result = func(*args, **kwargs)  # Call the function
            end_time = time.time()  # Record the end time
            execution_time = end_time - start_time  # Calculate execution time

            # Log the execution time using the provided logger
            if logger:
                logger.log("info", f"> Function(s): '[{func.__name__}]'. Runtime: [<OK> in {execution_time:.4f} seconds]. Mode [Sync]. Environment: [{func.__module__}].")
            else:
                print("No logger provided. Execution time will not be logged.")
                print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
            
            return result
        return wrapper
    return decorator

def async_timer(logger=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()  # Record the start time
            result = await func(*args, **kwargs)  # Await the async function
            end_time = time.time()  # Record the end time
            execution_time = end_time - start_time  # Calculate execution time

            # Log the execution time using the provided logger
            if logger:
                logger.log("info", f"> Function(s): '[{func.__name__}]'. Runtime: [<OK> in {execution_time:.4f} seconds]. Mode [Async]. Environment: [{func.__module__}].")
            else:
                print("No logger provided. Execution time will not be logged.")
                print(f"Async function '{func.__name__}' executed in {execution_time:.4f} seconds")
            
            return result
        return wrapper
    return decorator