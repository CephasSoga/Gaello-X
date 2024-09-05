import asyncio
import aiohttp
from functools import wraps, partial
from typing import Dict, Callable

from utils.logs import Logger

async def async_generate(arg):
    """
    Asynchronously generates a value and yields it, then waits for 1 second before yielding the next value.
    
    :param arg: The value to be yielded.
    :type arg: Any
    
    :return: An asynchronous generator that yields the given value, then waits for 1 second before yielding the next value.
    :rtype: AsyncGenerator
    """
    yield arg
    await asyncio.sleep(1)

async def enumerate_async(async_gen):
    index = 0
    async for value in async_gen:
        yield index, value
        index += 1

async def quickFetchBytes(target: str, params: Dict = None, headers: Dict = None, logger: Logger = None):
    """
    Asynchronously fetches bytes from a given target URL using the aiohttp library.

    Args:
        target (str): The URL to fetch bytes from.
        params (Dict, optional): Query parameters to include in the request. Defaults to None.
        headers (Dict, optional): HTTP headers to include in the request. Defaults to None.
        logger (Logger, optional): Logger instance to log information. Defaults to None.

    Returns:
        bytes: The fetched bytes if the request is successful.
        None: If an error occurs while fetching the data.
    """
    if logger is not None:
        logger.log('info' ,f"Requesting URL: {target} with params: {params} and headers: {headers}")
    try:
        async with aiohttp.ClientSession() as session:
                    async with session.get(target, params=params, headers=headers) as response:
                        response.raise_for_status()
                        #render bytes
                        if logger:
                            logger.log('info', 'Request Successful')
                        return await response.content.read()
    except aiohttp.ClientError as e:
        if logger:
            logger.log('info', f"An error occurred while fetching data with params <{params}>", e)
        return None
    
async def quickFetchJson(target: str, params: Dict = None, headers: Dict = None, logger: Logger = None):
    """
    Asynchronously fetches JSON data from a given target URL using the aiohttp library.

    Args:
        target (str): The URL to fetch JSON data from.
        params (Dict, optional): Query parameters to include in the request. Defaults to None.
        headers (Dict, optional): HTTP headers to include in the request. Defaults to None.
        logger (Logger, optional): Logger instance to log information. Defaults to None.

    Returns:
        Dict: The fetched JSON data if the request is successful.
        None: If an error occurs while fetching the data.
    """
    if logger is not None:
        logger.log('info' ,f"Requesting URL: {target} with params: {params} and headers: {headers}")
    try:
        async with aiohttp.ClientSession() as session:
                    async with session.get(target, params=params, headers=headers) as response:
                        response.raise_for_status()
                        #render json
                        if logger:
                            logger.log('info', 'Request Successful')
                        return await response.json()
    except aiohttp.ClientError as e:
        if logger:
            logger.log('info', f"An error occurred while fetching data with params <{params}>", e)
        return None

def asyncWrap(func):
    """
    Wraps a synchronous function into an asynchronous one using `asyncio.run_in_executor`.

    Args:
        func (callable): The synchronous function to wrap.

    Returns:
        callable: The wrapped asynchronous function.

    Keyword Args:
        loop (asyncio.AbstractEventLoop, optional): The event loop to use. Defaults to `asyncio.get_event_loop()`.
        executor (concurrent.futures.Executor, optional): The executor to use. Defaults to `None`.

    Example:
    >>> import time
    >>> async_sleep = asyncWrap(time.sleep)

    >>> async def count(*args, **kwargs):
    >>>    print("func start")
    >>>    await async_sleep(1)
    >>>    print(args, kwargs)
    >>>    print("func end")
    >>>    return True


    >>> async def main():
    >>>     r = await count(1, 2, 3)
    >>>     print("res: ", r)

    >>>  "res":  True
    """
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run

async def ThreadRun(func: Callable, *args, **kwargs):
    """
    Runs a function in a separate thread and waits for its result.

    This is a convenient way to run I/O-bound operations without blocking the event loop.

    Args:
        func (callable): The function to run in a separate thread.
        *args: The positional arguments to pass to the function.
        **kwargs: The keyword arguments to pass to the function.

    Returns:
        Any: The result of the function.

    Example:
    >>> async def main():
    >>>     result = await ThreadRun(time.sleep, 1)
    >>>     print("result:", result)

    >>>  "result":  None
    """
    result = await asyncio.to_thread(func, *args, **kwargs)
    return result


def add(a, b):
    return [a for a in [a, b] if a == b]

async def main():
    import time
    result = await ThreadRun(add, 1, 3)
    print("result:", result)

if __name__ == "__main__":
    asyncio.run(main())