from datetime import datetime

def now():
    return datetime.now()

def time_(): 
    return now().time().strftime("%H:%M:%S")

def date():
    return now().date().strftime("%Y-%m-%d")