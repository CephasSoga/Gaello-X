import asyncio
import aiohttp

from typing import Dict
from utils.logs import Logger

async def async_generate(arg):
    yield arg
    await asyncio.sleep(1)

async def quickFetchBytes(target: str, params: Dict = None, headers: Dict = None, logger: Logger = None):
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