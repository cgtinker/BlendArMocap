'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

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
