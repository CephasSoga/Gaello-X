import os
import json
from typing import Callable

from app.windows.WarningDialog import Warning
from databases.mongodb.Common import mongoGet

def read_user_id() -> str:
    """
    Reads the user ID from the credentials file.

    This function reads the user ID from the credentials file located at "credentials/credentials.json" in the directory specified by the "APP_BASE_PATH" environment variable. The function first retrieves the base path using `os.getenv("APP_BASE_PATH")`. It then constructs the path to the credentials file using `os.path.join(base_path, "credentials/credentials.json")`. If the file is found, it is opened in read mode and the JSON data is loaded using `json.load()`. The user ID is retrieved from the loaded JSON data using `credentials.get('id')`. If the user ID is not found, an empty string is returned. If any exception occurs during the process, the exception is raised.

    Returns:
        str: The user ID retrieved from the credentials file.

    Raises:
        FileNotFoundError: If the credentials file is not found.
        Exception: If any other exception occurs during the process.
    """
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
    """
    Reads the authorization level from the credentials file.

    This function reads the authorization level from the credentials file located at "credentials/credentials.json" in the directory specified by the "APP_BASE_PATH" environment variable. The function first retrieves the base path using `os.getenv("APP_BASE_PATH")`. It then constructs the path to the credentials file using `os.path.join(base_path, "credentials/credentials.json")`.

    The function opens the credentials file using `open(credentials_path, 'r')` and loads the contents into a dictionary using `json.load(credentials_file)`. It retrieves the user email from the dictionary using `credentials.get('email', '')`.

    If a user email is found, the function calls the `mongoGet` function to retrieve a list of users from the "UsersAuth" database and "users" collection. It uses a large limit to ensure that the user is included in the returned range. It then filters the list of users to find the user with the matching email. If a matching user is found, it retrieves the authorization level from the user dictionary using `user.get('authorizationLevel', 0)` and returns it as an integer. If no matching user is found, it returns 0.

    If a `FileNotFoundError` is raised during the execution of the function, it returns 0. If any other exception is raised, it is re-raised using `raise(e)`.

    Returns:
        int: The authorization level of the user, or 0 if no user email is found or if the credentials file is not found.
    """
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
                return int(user.get('authorizationLevel', 0))
        return 0
    except FileNotFoundError:
        return 0
    
    except Exception as e:
        raise(e)


def exec_with_reserve(req: int, func: Callable,  *args, **kwargs):
    """
    Executes a function only if the user has the required authorization level.

    Parameters:
        req (int): The required authorization level.
        func (Callable): The function to be executed.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Raises:
        ValueError: If the user's access key is missing.
        PermissionError: If the user doesn't have the permissions to access the resource.
    """
    level = read_auth_level()
    if level >= req:
        func(*args, **kwargs)
    elif level == 0:
        raise ValueError("It seems that your access key is missing. Create a new account, login or subscribe to a plan.")
    else:
        raise PermissionError("You don't have the permissions to access this resource.")
    

def handleAuth(req: int, func: Callable,  *args, **kwargs):
    """
    Executes the given function with the provided arguments and keyword arguments, if the user has the required authorization level.

    Args:
        req (int): The required authorization level.
        func (Callable): The function to be executed.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Raises:
        PermissionError: If the user does not have the required authorization level.
        ValueError: If the user's access key is missing.

    Returns:
        None: If an exception is raised during execution.
    """
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
