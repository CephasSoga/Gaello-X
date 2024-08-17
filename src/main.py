import os
import sys
import subprocess
import threading

# Help pyinstaller detect used packages
# 1- Pypi packages
import asyncio, PyQt5, qasync, pyqtspinner, json, pathlib, requests, aiohttp, audioread, bcrypt, numpy, plotly, pymongo, pyaudio, waitress, dotenv, flask
# 2- Custom packages
import janine
import client
import app
import databases
import models
import utils
# 3- Dispatched imports for pyqt5
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
#4 - Dispatched imports from janine
from janine import RichText, RichAudio, RichFile, RichVision, BaseRemote, BaseUtility
#5 - Dispatched imports from utils
from utils.logs import Logger
#6- Dispatched imports from databases
from databases.mongodb import Common,  UsersAuth, Operations, JanineDB
#7- Dispatched imports from models
from models.janine import JanineModel
from models.api.requests import RequestManager
from models.api import app
from models.api.app import Application as FlaskApplication
from models.reader.cache import CredentialsReader, cached_credentials
#8- Dispatched imports from app
from app.windows import *
from app.handlers import HashWorker, ExportAssets, Patterns, ShortLiveSeries
from app.inferential import ExportInsights, Insights
#9- Dispatched imports from api



from client.client import Client
from utils.system import restoreSystemPath
from utils.paths import getFrozenPath, getFrozenPath2

_cwd = os.getcwd()
main_logger = Logger("Main")
main_logger.log("info", "Starting the application...")
main_logger.log("info", f"Current working directory: {_cwd}")


def thread_exec(func):
    thread = threading.Thread(target=func)
    thread.setDaemon(True)  # Daemonize the thread, so it will exit when the main program exits.
    thread.start()

def exec_client():
    """
    Executes the client by creating an instance of the Client class and calling its run method.

    This function does not take any parameters.

    This function does not return any values.
    """
    cl = Client()
    cl.run()

def exec_api():
    api = FlaskApplication()
    try:
        thread_exec(
            lambda: api.run(threaded=False, host='0.0.0.0', port=5000, debug=True),
        )
    except Exception as e:
        main_logger.log("error", "Failed to start the API", e)

def exec_all():
    """
    A function that executes both the API and client components in a try-finally block.
    """
    try:
        exec_api()
    finally:
        exec_client()

if __name__ == "__main__":

    # Calls the exec_all function to execute both the API and client components.
    exec_all()
