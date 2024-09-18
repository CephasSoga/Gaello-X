import os
import sys
import ctypes
import subprocess
import threading

# 0-.
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
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
from PyQt5.QtGui import QGuiApplication
#4 - Dispatched imports from janine
from janine import RichText, RichAudio, RichFile, RichVision, BaseRemote, BaseUtility
#5 - Dispatched imports from utils
from utils.logs import Logger
#6- Dispatched imports from databases
from databases.mongodb import UsersAuth, Operations, JanineDB
#7- Dispatched imports from models
from models.janine import JanineModel
from models.api.requests import RequestManager
from models.api import app
from models.api.app import Application as FlaskApplication
from models.reader.cache import CredentialsReader, cached_credentials
#8- Dispatched imports from app
from app.windows import *
from app.versions.control import *
from app.handlers import HashWorker, ExportAssets, Patterns, ShortLiveSeries
from app.config import scheduler, balancer, fonts, renderer
#9- Dispatched imports from ...
from client.client import Client
from utils.system import restoreSystemPath
from utils.paths import getFrozenPath, getFrozenPath2
from utils.appHelper import getScreenSize, getDPI
from utils.envHandler import getenv
from utils.logs import Logger, timer

_cwd = os.getcwd()
main_logger = Logger("Main")
main_logger.log("info", "Starting the application...")
main_logger.log("info", f"Current working directory: {_cwd}")

@timer(logger=main_logger)
def system_check(resolution_check_enabled: bool = True):
    BASE_DPI = 144
    BASE_PROPS = 1920, 1080
    dpi = getDPI()
    scaling_factor = dpi / 96.0
    screen_props = getScreenSize()
    main_logger.log("info", f"Sytem:\n\tDPI resolution: {dpi}, \n\tScreen resolution: {screen_props}")
    if resolution_check_enabled:
        if dpi!= BASE_DPI or (
            screen_props[0]!= BASE_PROPS[0] or scaling_factor * screen_props[0] != BASE_PROPS[0]
        ) or (
            screen_props[1]!= BASE_PROPS[1] or scaling_factor * screen_props[1] != BASE_PROPS[1]
        ):
            main_logger.log(
                "warning", 
                "The optimal requirements for the application's DPI or screen resolution are not met. Automatically adjusting... Please be warned that this might result in degraded visuals"
            )
        else:
            main_logger.log("info", "The optimal requirements for the application's DPI or screen resolution are met. No adjustments needed.")

@timer(logger=main_logger)
def create_mongo_connection():
    uri = getenv("MONGO_URI")

    # Create a new client and connect to the server
    mongo_client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        mongo_client.admin.command('ping')
        main_logger.log("info", "MongoDB connected successfully!")
        return mongo_client
    except Exception as e:
        main_logger.log("error", "MongoDB connection attempt failed", e)
        return None

@timer(logger=main_logger)
def binary_exec():
    subprocess.Popen([r".\binary.bat"], shell=True)


def thread_exec(func):
    thread = threading.Thread(target=func)
    thread.setDaemon(True)  # Daemonize the thread, so it will exit when the main program exits.
    thread.start()

def exec_client():
    try:
        mongo_client = create_mongo_connection()
        if not mongo_client:
            return
        cl = Client(connection=mongo_client)
        cl.run()
    except Exception as e:
        main_logger.log("error", "Failed to start the client", e)

def exec_api():
    api = FlaskApplication()
    try:
        thread_exec(
            lambda: api.run(threaded=False, host='0.0.0.0', port=5000, debug=True),
        )
    except Exception as e:
        main_logger.log("error", "Failed to start the API", e)

@timer(logger=main_logger)
def exec_all():
    try:
        system_check(resolution_check_enabled=False)
    except SystemExit:
        return
    except Exception:
        main_logger.log("error", "Unexpected error", exc_info=True)
        return
    
    try:
        print("Applying binaries...")
        binary_exec()
        #print("Skipping binaries...")
    except (SystemExit, SystemError) as sys_err:  # Exits the program if the binary cannot be executed:
        main_logger.log("error", "System error while executing the binary. Returning...", sys_err)
        return
    except KeyboardInterrupt:  # Exits the program if the user presses Ctrl+C:
        main_logger.log("error", "User interrupted the program. Returning...")
        return
    except Exception as e:
        main_logger.log("error", "Failed to execute the binary. Returning...", e)
        return
    
    try:
        main_logger.log("info", "Starting the Gaello Application...")
        exec_api()
    except Exception as e:
        main_logger.log("error", "Failed to start the API and Application. Returning...", e)
        raise  # Re-raise the exception to propagate it to the caller.
    finally:
        main_logger.log("info", "Launching GUI...")
        exec_client()

if __name__ == "__main__":
    # Calls the exec_all function to execute both the API and client components.
    exec_all()

