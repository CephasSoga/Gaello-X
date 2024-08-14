from collections import deque

from flask import Flask, render_template, request, jsonify
from waitress import serve

#from app.windows.AuthHandler import read_user_id
from utils.logs import Logger
from models.reader.cache import cached_credentials


app = Flask("Janine-Endpoint")

logger = Logger("Janine-Endpoint")
print("API: Credentials: ", cached_credentials)

MAX_QUEUE_SIZE = 1000
successfulRequetsQueue = deque(maxlen=MAX_QUEUE_SIZE)
ID = cached_credentials.get('id', '')
EMAIL = cached_credentials.get('email', '')

if not ID or not EMAIL:
    logger.log('error', 'Empty user credentials.', ValueError('User credentials not found in cache.'))

@app.route(f'/janine/index/{ID}-{EMAIL}', methods=['POST'])
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

@app.route(f'/janine/index/{ID}-{EMAIL}', methods=['GET'])
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
        try:
            logger.log('info', 'Starting Janine-Endpoint on plain Flask...')
            app.run(debug=True)
        except Exception as e:
            logger.log('error', f'Error starting Janine-Endpoint: {e}', ValueError('Error starting Janine-Endpoint'))
            logger.log("info", "Shifting to waitress server")
            try:
                serve(app, host="0.0.0.0", port=5000)
                logger.log("info", "Successfully shifted to waitress server")
            except Exception as e:
                logger.log('error', f'Error starting waitress server: {e}', ValueError('Error starting waitress server'))
                logger.log('error', 'Error starting Janine-Endpoint. Please check the logs for more information.')


if __name__ == "__main__":
    Application.run()