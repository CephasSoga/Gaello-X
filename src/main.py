import os
import subprocess

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


from client.client import Client
from utils.system import restoreSystemPath

#Switch to rootDir, then to app Dir to handle relative paths
currentDir = os.path.dirname(__file__)
parentDir = currentDir #os.path.dirname(currentDir)
rootDir = os.path.dirname(parentDir)
os.chdir(os.path.join(rootDir, 'app')) #os.chdir(rootDir)

def exec_client():
    """
    Executes the client by creating an instance of the Client class and calling its run method.

    This function does not take any parameters.

    This function does not return any values.
    """
    cl = Client()
    cl.run()

def exec_api():
    """
    Executes the API by running a separate Python process that executes the app.py file in the models/api directory.

    This function does not take any parameters.

    This function does not return any values.
    """
    subprocess.Popen(['python', f'{rootDir}/models/api/app.py'])
    # Ensure the system’s default DLL search path on Windows systems is restored
    restoreSystemPath()

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
