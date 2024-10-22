import json
import aiohttp
from typing import Any, List, Dict

from models.reader.cache import cached_credentials
from models.config.args import EndpointsArgs
from utils.logs import Logger

logger = Logger("Request-Manager")

ID = cached_credentials.get('id', '')
EMAIL = cached_credentials.get('email', '')
if not ID or not EMAIL:
    logger.log('warning', 'Empty user credentials.', ValueError('User credentials not found in cache.'))
PATH = f'janine/index/{ID}-{EMAIL}'

def serialize(obj):
    """
    Serializes an object into a JSON string representation.

    Args:
        obj (Any): The object to be serialized.

    Returns:
        str: The JSON string representation of the object.

    Raises:
        TypeError: If the object cannot be serialized.
        """
    return json.dumps(obj, default=lambda o: o.__dict__, indent=4)

def forceSerialize(obj):
    """
    Serializes an object into a JSON string representation.

    Args:
        obj (Any): The object to be serialized.

    Returns:
        str: The JSON string representation of the object.

    Raises:
        TypeError: If the object cannot be serialized.
            - If the object is not a string and does not have a `__str__` method, a TypeError is raised.
            - If the object is a string but cannot be serialized, a TypeError is raised.

    Notes:
        - This function handles RepeatedComposite or other known non-serializable types by attempting to convert them to strings.
        - If the object cannot be serialized after attempting to convert it to a string, a TypeError is raised.
    """
    try:
        return serialize(obj)
    except TypeError:
        # Handle RepeatedComposite or other known non-serializable types here
        if hasattr(obj, '__str__'):
            try:
                return serialize(str(obj, encoding="UTF-8"))
            except TypeError:
                pass

        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


class RequestManager:
    """
    A class used to manage HTTP requests to a specified URL.

    Attributes
    ----------
    url : str
        The URL to which the requests will be made.
    headers : dict
        The headers to be included in the requests.
    logger : Logger
        An instance of the Logger class for logging events.

    Methods
    -------
    post(message: Dict[str, Any]) -> None
        Sends a POST request to the specified URL with the given message.

    get() -> List
        Sends a GET request to the specified URL and returns the response data.

    getLast() -> Dict
        Sends a GET request to the specified URL, retrieves the response data,
        and returns the last item in the data.
    """
    def __init__(
            self, 
            protocol:str=EndpointsArgs.REQ_PROTOCOL, 
            ip:str=EndpointsArgs.REQ_HOST, 
            port:str=EndpointsArgs.REQ_PORT, 
            path:str=PATH
        ):
        """
        Constructs all the necessary attributes for the RequestManager object.

        Parameters
        ----------
        protocol : str, optional
            The protocol to be used in the URL (default is 'http').
        ip : str, optional
            The IP address to be used in the URL (default is '127.0.0.1').
        port : str, optional
            The port to be used in the URL (default is '5000').
        path : str, optional
            The path to be appended to the URL (default is 'janine/index/{id}-{email}').
        """
        self.url = f'{protocol}://{ip}:{port}/{path}'
        self.headers = {'Content-Type': 'application/json'}
        self.logger = Logger('Janine-API-Resquests')

    async def post(self, message: Dict[str, Any]) -> None:
        """
        Sends a POST request to the specified URL with the given message.

        Parameters:
        message : Dict[str, Any]
            The message to be sent in the POST request.

        Returns:
           None
        """
        body = forceSerialize(message)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=self.headers, data=body) as response:
                    response.raise_for_status()
                    responseJson = await response.json()
                    self.logger.log('info', f"POST Request Successfull. Status Code: {response.status}")
        except aiohttp.ClientError as ce:
            self.logger.log('error', f"POST Request Failed On Client Side. Status Code: {response.status}", ce)
            return
        
        except Exception as e:
            self.logger.log('error', f"POST Request Failed On Either Client or Server Side. Status Code: {response.status}", e)
            return
        
    async def get(self) -> List:
        """
        Sends a GET request to the specified URL and returns the response data.

        Returns:
            List: The response data from the GET request.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    self.logger.log('info', f"GET Request Successfull. Status Code: {response.status}")
                    return data
        except aiohttp.ClientError as ce:
            self.logger.log('error', f"GET Request Failed On Client Side. Status Code: {response.status}", ce)
            return []
        except Exception as e:
            self.logger.log('error', f"GET Request Failed On Either Clide or Server Side. Status Code: {response.status}", ce)
            return []
        
    async def getLast(self) -> Dict:
        """
        Sends a GET request to the specified URL, retrieves the response data,
        and returns the last item in the data.

        Returns
        -------
        Dict
            The last item in the response data.
        """
        try:
            response = await self.get()
            if response:
                return response[-1]
            else:
                self.logger.log('error', f"No data available")
                return {}
        except IndexError as ie:
            self.logger.log('error', f"Either data is unavailable or length is too short", ie)