import os
import subprocess

# Specify the port you want to close
port = 8888

# Find the process ID (PID) using the port
try:
    result = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True)
    lines = result.decode().splitlines()

    for line in lines:
        parts = line.split()
        if parts[-1].isdigit():
            pid = int(parts[-1])

            # Kill the process
            os.kill(pid, 9)
            print(f"Closed port {port} by terminating process {pid}")

except subprocess.CalledProcessError:
    print(f"No process is using port {port}")
except Exception as e:
    print(f"An error occurred: {e}")
