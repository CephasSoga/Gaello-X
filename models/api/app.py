import os
import json
from collections import deque
from typing import Tuple

from flask import Flask, render_template, request, jsonify
from waitress import serve

#from app.windows.AuthHandler import read_user_id
from utils.logs import Logger
from utils.envHandler import getenv

currentDir = os.path.dirname(__file__)
parentDir = os.path.dirname(currentDir)
rootDir = os.path.dirname(parentDir)
os.chdir(rootDir)

app = Flask(__name__)

logger = Logger(__name__)

MAX_QUEUE_SIZE = 1000
successfulRequetsQueue = deque(maxlen=MAX_QUEUE_SIZE)

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


@app.route(f'/janine/index/{id}-{email}', methods=['POST'])
def post():
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
    return jsonify(list(successfulRequetsQueue)), 200

@app.route('/janine')
def index():
    return render_template('index.html')

class Application:

    @staticmethod
    def run():
        app.run(debug=True)

if __name__ == "__main__":
    Application.run()