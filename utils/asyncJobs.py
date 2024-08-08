import asyncio
import aiohttp

from typing import Dict
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