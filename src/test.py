import time

def timer(func, logger=None):
    """
    A decorator that logs the time taken to execute a function.

    Args:
        func: The function to be timed.
        logger: An optional logger to log the time taken.

    Returns:
        The result of the function.
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        if logger:
            logger.log("info", f"{func.__name__} took: {end - start:.4f} seconds to complete.")
        else:
            print(f"{func.__name__} took: {end - start:.4f} seconds to complete.")
        return result
    return wrapper

@timer
def factorial(n):
    """
    Calculate the factorial of a number.

    Args:
        n: The number to calculate the factorial of.

    Returns:
        The factorial of the number.
    """
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


print(factorial(10))

import time

def timer(func, logger: Logger|None = None):
    """
    A decorator that logs the time taken to execute a synchronous function.

    Args:
        func: The function to be timed.
        logger: An optional logger to log the time taken.

    Returns:
        The result of the function.
    """

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        if logger:
            logger.log("info", f"{func.__name__} took: {end - start:.4f} seconds to complete.")
        else:
            print(f"{func.__name__} took: {end - start:.4f} seconds to complete.")
        return result
    return wrapper


def async_timer(func, logger: Logger|None = None):
    """
    A decorator that logs the time taken to execute an asynchronous function.

    Args:
        func: The function to be timed.
        logger: An optional logger to log the time taken.

    Returns:
        The result of the function.
    """

    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        if logger:
            logger.log("info", f"{func.__name__} took: {end - start:.4f} seconds to complete.")
        else:
            print(f"{func.__name__} took: {end - start:.4f} seconds to complete.")
        return result
    return wrapper