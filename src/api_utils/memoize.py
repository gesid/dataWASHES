from collections.abc import Callable
from functools import wraps


def memoize(func: Callable):
    cache: dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal cache
        key_cache = str(args) + str(kwargs)
        if key_cache not in cache:
            cache[key_cache] = func(*args, **kwargs)
        return cache[key_cache]

    return wrapper
