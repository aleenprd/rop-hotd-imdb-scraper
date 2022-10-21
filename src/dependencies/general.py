"""Miscelaneous/general utility methods/classes."""


from typing import Callable
from time import time


def timing(f: Callable) -> None:
    """Decorates method by printing runtime in minutes.

    Args:
        f (callable): a function/method.
    """
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        exec_time = round((te - ts) / 60, 4)
        print(f"\nExecution time: {exec_time} minutes.")

    return wrap
