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

