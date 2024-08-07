import os
import subprocess

from client.client import Client

#Switch to rootDir, then to app Dir to handle relative paths
currentDir = os.path.dirname(__file__)
parentDir = currentDir #os.path.dirname(currentDir)
rootDir = os.path.dirname(parentDir)
os.chdir(os.path.join(rootDir, 'app')) #os.chdir(rootDir)

def exec_client():
    cl = Client()
    cl.run()

def exec_api():
    subprocess.Popen(['python', f'{rootDir}/models/api/app.py'])

def exec_all():
    try:
        exec_api()
    finally:
        exec_client()

if __name__ == "__main__":
    exec_all()
