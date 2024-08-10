import os
import json
from collections import deque
from typing import Tuple

from flask import Flask, render_template, request, jsonify
from waitress import serve

#from app.windows.AuthHandler import read_user_id
from utils.logs import Logger
from utils.envHandler import getenv


app = Flask("Janine-Endpoint")

logger = Logger("Janine-Endpoint")

MAX_QUEUE_SIZE = 1000
successfulRequetsQueue = deque(maxlen=MAX_QUEUE_SIZE)

def read_user_endpoint() -> Tuple[str, str] | None:
    """
    Reads the user endpoint from the credentials file.

    This function retrieves the base path using the "APP_BASE_PATH" environment variable.
    It then constructs the path to the credentials file and attempts to open it.
    If the file is found, it loads the JSON data and returns the user ID and email.
    If the file is not found, it returns None.
    If any other exception occurs during the process, it is re-raised.

    Returns:
        Tuple[str, str] | None: A tuple containing the user ID and email, or None if the file is not found.
    """
    base_path = getenv("APP_BASE_PATH")
    credentials_path = os.path.join(base_path, "credentials", "credentials.json")
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


@app.route(f'/janine/index/{id}-{email}', methods=['POST'])
def post():
    """
    Handle a POST request to the '/janine/index/{id}-{email}' endpoint.

    This function is a route handler for the '/janine/index/{id}-{email}' endpoint, which is decorated with the `@app.route` decorator. It accepts POST requests and expects a JSON payload in the request body.

    Parameters:
        None

    Returns:
        - If the request body contains JSON data, the function appends a dictionary containing the request method, headers, and body to the `successfulRequetsQueue` deque. It then returns a JSON response with the last element of the `successfulRequetsQueue` deque and a status code of 201.
        - If the request body is empty, the function returns a JSON response with an error message and a status code of 400.
    """
    data = request.json
    if data:
        successfulRequetsQueue.append({
            "method": "POST",
            "headers": dict(request.headers),
            "body": data,
        })
        return jsonify(successfulRequetsQueue[-1]), 201
    else:
        return jsonify({"error": "No data provided in the request body"}), 400

@app.route(f'/janine/index/{id}-{email}', methods=['GET'])
def get():
    """
    Handle a GET request to the '/janine/index/{id}-{email}' endpoint.

    This function is a route handler for the '/janine/index/{id}-{email}' endpoint, which is decorated with the `@app.route` decorator. It accepts GET requests and returns a JSON response containing a list of dictionaries representing the successful requests that have been made to the endpoint. The status code of the response is always 200.

    Parameters:
        None

    Returns:
        Tuple[dict, int]: A tuple containing a JSON response with a list of successful requests and a status code of 200.
        """
    return jsonify(list(successfulRequetsQueue)), 200

@app.route('/janine')
def index():
    """
    Handle a GET request to the '/janine' endpoint.

    This function is a route handler for the '/janine' endpoint, which is decorated with the `@app.route` decorator. It accepts GET requests and returns a rendered HTML template.

    Parameters:
        None

    Returns:
        str: The rendered HTML template.
    """
    return render_template('index.html')

class Application:

    @staticmethod
    def run():
        app.run(debug=True)

if __name__ == "__main__":
    Application.run()