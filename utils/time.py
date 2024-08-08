from datetime import datetime

def now():
    """
    A function that returns the current date and time.
    """
    return datetime.now()

def time_(): 
    """
    Returns the current time in the format "%H:%M:%S".

    This function uses the `datetime.now()` function to get the current date and time, and then calls the `time()` method on the resulting `datetime` object to get the current time. Finally, the `strftime()` method is called on the resulting `time` object to format it as a string in the format "%H:%M:%S".

    Returns:
        str: The current time in the format "%H:%M:%S".
    """
    return now().time().strftime("%H:%M:%S")

def date():
    """
    Returns the current date in the format 'YYYY-MM-DD'.

    :return: A string representing the current date.
    :rtype: str
    """
    return now().date().strftime("%Y-%m-%d")