import os
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
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def  getTargetFilesWithDelay(pattern:str, delay:str=1) -> list:
    time.sleep(delay)
    return glob.glob(pattern)

def latestTargetFileWithDelay(pattern:str, delay:str=1) ->str:
    files = getTargetFilesWithDelay(pattern, delay)
    return max(files, key=os.path.getctime)


def latestTargetFilesWithPolling(pattern:str, timeout:int=5, interval:float=0.5):
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
    return pathStr.replace("\\", "\\\\")

