import traceback
from functools import wraps
from time import time
import logging


def timeit(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        runtime = end - start
        print(f"function: {func.__name__}(args: {args}, kwargs: {kwargs})\ntook: {round(runtime, 5)} sec\n")
        return result
    return wrap


def except_error(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            logging.error(traceback.format_exc())
    return wrap

