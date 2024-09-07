import os
import json
import asyncio
from typing import Callable

from pymongo.mongo_client import MongoClient

from app.windows.WarningDialog import Warning
from utils.databases import mongoGet
from utils.paths import getFileSystemPath
from utils.envHandler import getenv
from utils.asyncJobs import asyncWrap

def sync_read_user_cred_file() -> dict:
    base_path = getFileSystemPath(getenv("APP_BASE_PATH"))
    credentials_path = os.path.join(base_path, "credentials", "credentials.json")
    try:
        with open(credentials_path, 'r') as credentials_file:
            credentials: dict = json.load(credentials_file)

        user_email = credentials.get('email', '')
        user_id = credentials.get('id', '')

        return {'id': user_id, 'email': user_email}
    except FileNotFoundError:
        raise FileNotFoundError("Credentials file not found")
    except Exception as e:
        raise(e)
    
async def read_user_cred_file() -> dict:
    async_read_wrap = asyncWrap(sync_read_user_cred_file)
    file_res: dict = async_read_wrap()
    return await file_res

def read_user_id() -> str: 
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        file_res = loop.run_until_complete(read_user_cred_file())
        #loop.close()
        return file_res.get('id', '')
    except FileNotFoundError:
        return None
    except Exception as e:
        raise(e)



async def read_auth_level(connection: MongoClient) -> int:

    try:
        file_res = await read_user_cred_file()
        if not file_res:
            return 0

        user_email = file_res.get('email', '')

        if user_email:
            asyncMongoGet = asyncWrap(mongoGet)
            users = await asyncMongoGet(database='UsersAuth', collection="users", limit=int(1e7), connection=connection) # Use a verly large limit to avoid returned range not including user

            this_user = [user for user in users if user['user']['email'] == user_email]

            user = this_user[0] if this_user else None
            if user:
                return int(user.get('authorizationLevel', 0))
        return 0
    except FileNotFoundError:
        return 0
    
    except Exception as e:
        raise(e)


async def exec_with_reserve(connection: MongoClient, req: int, func: Callable,  *args, **kwargs):
    level = await read_auth_level(connection=connection)
    #loop.close()
    if level >= req:
        func(*args, **kwargs)
    elif level == 0:
        raise ValueError("It seems that your access key is missing. Create a new account, login or subscribe to a plan.")
    else:
        raise PermissionError("You don't have the permissions to access this resource.")
    

async def handleAuth(connection: MongoClient, req: int, func: Callable,  *args, **kwargs):

    try:
        await exec_with_reserve(connection, req, func, *args, **kwargs)
    except PermissionError as e:
        msg = Warning('Permission Denied', str(e))
        msg.exec()
        return
    except ValueError as e:
        msg = Warning('Login not effective', str(e))
        msg.exec()
        return


if __name__ == '__main__':
    import time
    s = time.perf_counter()
    try:
        exec_with_reserve(4, print, "Hello World")
    except Exception as e:
        print(e)
    e =  time.perf_counter()
    print(f"Time elapsed: {e-s:.4f} seconds")