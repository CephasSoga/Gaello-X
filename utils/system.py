import os
import socket
import subprocess

def get_ipv4_address():
    """
    Retrieves the IPv4 address of the current machine.

    Returns:
        str: The IPv4 address of the current machine.

    Raises:
        socket.error: If the connection to the external server fails.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipv4_address = s.getsockname()[0]
    s.close()

    return ipv4_address

def get_ipconfig():
    """
    Executes the 'ipconfig' command using the subprocess module and returns the output as a decoded string.

    Returns:
        str: The output of the 'ipconfig' command as a decoded string.
    """
    return subprocess.check_output('ipconfig').decode('utf-8')

def restoreSystemPath():
    """
    This function is designed to restore the system's default DLL search path on Windows systems.

    Here's a breakdown of the code:

    1.The function starts by importing the necessary modules: sys and ctypes.

    2.It checks if the current platform is Windows (sys.platform == "win32").

    3.If the platform is Windows, it imports the ctypes module and uses the windll.kernel32.SetDllDirectoryA() function to 
    restore the system's default DLL search path. The None argument passed to this function indicates that the default DLL search
    path should be used.

    This function is useful when working with DLLs and libraries in Python on Windows, 
    as it ensures that the system's default DLL search path is used, which can help resolve issues related to DLL loading.
    
    In the context of pyinstaller,S this function should be run when a subprocess has benn called or on appliaction startup.
    See: https://github.com/pyinstaller/pyinstaller/issues/3795
    """
    import sys
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryA(None)


def killPortProcess(port: int | str):
    # Find the process ID (PID) using the port
    """
    Kills the process using the specified port.

    This function finds the process ID (PID) associated with the specified port and terminates the process.

    Parameters:
        port (int): The port number to identify the process.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If no process is using the specified port.
        Exception: If an error occurs while executing the command to find the process ID.

    """
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


