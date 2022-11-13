"""Miscelaneous/general utility methods/classes."""


from typing import Callable
from time import time
from typing import List


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


def flatten(l: List[List]) -> List:
    """Flatten a list of lists.

    Args:
        l (List): a list of lists.

    Returns:
        List: a flattened list.
    """
    return [item for sublist in l for item in sublist]
