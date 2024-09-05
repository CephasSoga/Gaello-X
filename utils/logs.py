import logging
from typing import Any
from pathlib import Path

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



import time

def timer(func):
    """
    A decorator that logs the time taken to execute a synchronous function.

    Args:
        func: The function to be timed.

    Returns:
        The result of the function.
    """

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"\n*** Runtime check: {func.__name__} took: {end - start:.4f} seconds to complete.\n")
        return result
    return wrapper


def async_timer(func):
    """
    A decorator that logs the time taken to execute an asynchronous function.

    Args:
        func: The async function to be timed.

    Returns:
        The result of the function.
    """

    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took: {end - start:.4f} seconds to complete.\n")
        return result
    return wrapper