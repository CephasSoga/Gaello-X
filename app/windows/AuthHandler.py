import os
import json
from typing import Callable

from app.windows.WarningDialog import Warning
from databases.mongodb.Common import mongoGet

def read_user_id() -> str:
    base_path = os.getenv("APP_BASE_PATH")
    credentials_path = os.path.join(base_path, "credentials/credentials.json")
    try:
        with open(credentials_path, 'r') as credentials_file:
            credentials = json.load(credentials_file)

        return credentials.get('id', '')
    except FileNotFoundError:
        return None
    except Exception as e:
        raise(e)


def read_auth_level() -> int:
    base_path = os.getenv("APP_BASE_PATH")
    credentials_path = os.path.join(base_path, "credentials/credentials.json")
    try:
        with open(credentials_path, 'r') as credentials_file:
            credentials = json.load(credentials_file)

        user_email = credentials.get('email', '')

        if user_email:
            users = mongoGet(database='UsersAuth', collection="users", limit=int(1e7)) # Use a verly large limit to avoid returned range not including user

            this_user = [user for user in users if user['user']['email'] == user_email]

            user = this_user[0] if this_user else None
            if user:
                return int(user.get('authorisationLevel', 0))
        return 0
    except FileNotFoundError:
        return 0
    
    except Exception as e:
        raise(e)


def exec_with_reserve(req: int, func: Callable,  *args, **kwargs):
    level = read_auth_level()
    if level >= req:
        func(*args, **kwargs)
    elif level == 0:
        raise ValueError("It seems that your access key is missing. Create a new account, login or subscribe to a plan.")
    else:
        raise PermissionError("You don't have the permissions to access this resource.")
    

def handleAuth(req: int, func: Callable,  *args, **kwargs):
    try:
        exec_with_reserve(req, func, *args, **kwargs)
    except PermissionError as e:
        msg = Warning('Permission Denied', str(e))
        msg.exec()
        return
    except ValueError as e:
        msg = Warning('Login not effective', str(e))
        msg.exec()
        return


# Test the function with different levels of access
if __name__ == '__main__':
    exec_with_reserve(0, print, "Hello World")
    exec_with_reserve(1, print, "Hello World")
    exec_with_reserve(2, print, "Hello World")
    exec_with_reserve(3, print, "Hello World")