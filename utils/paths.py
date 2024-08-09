import os
import sys
import time
import glob
from pathlib import Path

from typing import Union

def constructPath(basePath: Path, *pathsParts: Union[str, Path]) -> Path:
    """
    Constructs a path by appending path_parts to the base_path.
    """
    return basePath.joinpath(*pathsParts)


def getBasePath(file: Path, level: int) -> Path:
    """
    Returns the base path of the project by moving up the specified number of directory levels 
    from the current file's location.

    Args:
        level (int): The number of directory levels to move up from the current file's location.

    Returns:
        Path: The resulting base path after moving up the specified number of levels.
    """
    # Resolve the path of the current file
    basePath = file.resolve()
    
    # Move up 'level' directories
    for _ in range(level):
        basePath = basePath.parent

    return basePath


def forcePath(path: Path):
    """
    Create the parent directory of the given path if it does not already exist.

    Args:
        path (Path): The path for which the parent directory needs to be created.

    Returns:
        None: This function does not return anything.

    Raises:
        None: This function does not raise any exceptions.
    """
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def  getTargetFilesWithDelay(pattern:str, delay:str=1) -> list:
    """
    Retrieves a list of files matching the given pattern after waiting for the specified delay.

    Parameters:
        pattern (str): The pattern to match against file names.
        delay (str, optional): The delay in seconds before retrieving the files. Defaults to 1.

    Returns:
        list: A list of file paths matching the pattern.
    """
    time.sleep(delay)
    return glob.glob(pattern)

def latestTargetFileWithDelay(pattern:str, delay:str=1) ->str:
    """
    Retrieves the latest file matching the given pattern after waiting for the specified delay.

    Args:
        pattern (str): The pattern to match against file names.
        delay (str, optional): The delay in seconds before retrieving the files. Defaults to 1.

    Returns:
        str: The path of the latest file matching the pattern.
    """
    files = getTargetFilesWithDelay(pattern, delay)
    return max(files, key=os.path.getctime)


def latestTargetFilesWithPolling(pattern:str, timeout:int=5, interval:float=0.5):
    """
    Retrieves the latest file matching the given pattern within a specified time frame.

    Args:
        pattern (str): The pattern to match against file names.
        timeout (int, optional): The maximum time in seconds to search for the latest file. Defaults to 5.
        interval (float, optional): The time in seconds to wait between each check for the latest file. Defaults to 0.5.

    Returns:
        str: The path of the latest file matching the pattern, or None if no matching file is found within the specified time frame.
    """
    endTime = time.time() + timeout
    latest = None
    latestCTime = 0

    while time.time() < endTime:
        files = glob.glob(pattern)
        if files:
            tempLatest = max(files, key=os.path.getctime)
            tempLatestFileCTime = os.path.getctime(tempLatest)
            if tempLatestFileCTime > latestCTime:
                latest = tempLatest
                latestCTime = tempLatestFileCTime
        time.sleep(interval)
    return latest

def rawPathStr(pathStr: str):
    """
    Replaces all occurrences of a backslash ('\') in the given `pathStr` with a double backslash ('\\').

    Parameters:
        pathStr (str): The input string containing backslashes.

    Returns:
        str: The modified string with double backslashes.
    """
    return pathStr.replace("\\", "\\\\")

def resourcePath(relative_path):
    """
    Ref: https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    
    Returns the absolute path of a resource file.

    Parameters:
        relative_path (str): The relative path of the resource file.

    Returns:
        str: The absolute path of the resource file.

    Raises:
        Exception: If the base path cannot be determined.

    Example:
        >>> resource_path('config.ini')
        '/path/to/config.ini'
    """
    try:
        base_path = sys._MEIPASS # or sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getPath(filename: str):
    """
    Returns the full path to a given filename, taking into account the _MEIPASS attribute 
    if it exists in the sys module, which is typically the case for frozen applications.

    Parameters:
        filename (str): The name of the file for which to retrieve the full path.

    Returns:
        str: The full path to the given filename.
    """
    if hasattr(sys, "_MEIPASS"): # or sys._MEIPASS2
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename

