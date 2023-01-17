from __future__ import annotations
from functools import wraps
from time import time
from typing import Callable
from collections import deque


def timeit(func: Callable):
    avg = deque()

    @wraps(func)
    def wrap(*args, **kwargs):
        nonlocal avg

        start = time()
        result = func(*args, **kwargs)
        end = time()
        runtime = end - start
        avg.appendleft(runtime)
        if len(avg) > 30:
            avg.pop()

        print(f"function: {func.__name__}\ntook: {round(runtime, 5)} sec, avg of {len(avg)}: {sum(avg)/len(avg)} sec\n")
        return result

    return wrap


def fps(func: Callable):
    start = time()
    count = 0

    @wraps(func)
    def wrap(*args, **kwargs):
        nonlocal count
        nonlocal start
        res = func(*args, **kwargs)
        count += 1
        if time() - start >= 1:
            start = time()
            print(f"function '{func.__name__}' runs at {count} fps")
            count = 0

        return res

    return wrap
