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

