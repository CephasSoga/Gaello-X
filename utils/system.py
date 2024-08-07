import socket
import subprocess

def get_ipv4_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipv4_address = s.getsockname()[0]
    s.close()

    return ipv4_address

def get_ipconfig():
    return subprocess.check_output('ipconfig').decode('utf-8')

