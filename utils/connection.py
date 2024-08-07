import requests

def deviceIsConnected():
    try:
        response = requests.get("http://google.com")
        if response:
            return True
        else:
            return False
    except Exception:
        return False