import requests

def deviceIsConnected():
    """
    Checks if the device is connected to the internet.

    This function sends a GET request to the "http://google.com" URL and checks the response. If the response is successful (status code 200), it returns True. Otherwise, it returns False.

    Returns:
        bool: True if the device is connected to the internet, False otherwise.
    """
    try:
        response = requests.get("http://google.com")
        if response:
            return True
        else:
            return False
    except Exception:
        return False