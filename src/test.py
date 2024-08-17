import sys
import os
import subprocess

def resourcePath(relative_path):
    """
    Returns the absolute path of a resource file.
    """
    try:
        base_path = sys._MEIPASS  # or sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Resolve paths to Node.js and the server script
nodePath = resourcePath(os.path.join('resources', 'node', 'node.exe'))  # Adjust for your platform
serverPathStr = resourcePath(os.path.join('server', 'advanced.js'))
execPath = resourcePath(".")

# Running the subprocess with the bundled Node.js
try:
    process = subprocess.Popen(
        [nodePath, serverPathStr], 
        cwd=execPath, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error: {stderr}")
    else:
        print(f"Output: {stdout}")
except Exception as e:
    print(f"Failed to start subprocess: {e}")
