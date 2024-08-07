import os
import json
import aiohttp
from typing import Any, List, Dict, Tuple

from utils.logs import Logger
from utils.envHandler import getenv


logger = Logger(__name__)

def read_user_endpoint() -> Tuple[str, str] | None:
    base_path = getenv("APP_BASE_PATH")
    credentials_path = os.path.join(base_path, "credentials/credentials.json")
    try:
        with open(credentials_path, 'r') as credentials_file:
            credentials = json.load(credentials_file)

        return credentials.get('id', ''), credentials.get('email', '')
    except FileNotFoundError:
        return None
    except Exception as e:
        raise(e)

creds_details = read_user_endpoint()

if not creds_details:
    logger.log('error', "Empty credentials", ValueError("Empty credentials"))
    id, email = '', ''
else:
    id, email = creds_details


PROTOCOL = 'http'
IP = '127.0.0.1'
PORT = '5000'
PATH = f'janine/index/{id}-{email}'

def serialize(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, indent=4)

def forceSerialize(obj):
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
    def __init__(self, protocol:str=PROTOCOL, ip:str=IP, port:str=PORT, path:str=PATH):
        self.url = f'{protocol}://{ip}:{port}/{path}'
        self.headers = {'Content-Type': 'application/json'}
        self.logger = Logger('Janine-API-Resquests')

    async def post(self, message: Dict[str, Any]) -> None:
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
        try:
            response = await self.get()
            if response:
                return response[-1]
            else:
                self.logger.log('error', f"No data available")
                return {}
        except IndexError as ie:
            self.logger.log('error', f"Either data is unavailable or length is too short", ie)