from functools import wraps
import time
from typing import Callable

from autoconf import conf

def profile_func(func: Callable):
    """
    Time every function called in a class and averages over repeated calls for profiling likelihood functions.

    The timings are stored in the variable `_profiling_dict` of the class(s) from which each function is called,
    which are collected at the end of the profiling process via recursion.

    Parameters
    ----------
    func : (obj, grid, *args, **kwargs) -> Object
        A function which is used in the likelihood function..

    Returns
    -------
        A function that times the function being called.
    """

    @wraps(func)
    def wrapper(obj: object, *args, **kwargs):
        """
        Time a function and average over repeated calls for profiling an `Analysis` class's likelihood function. The
        time is stored in a `_profiling_dict` attribute.

        Returns
        -------
            The result of the function being timed.
        """

        if not conf.instance["general"]["profiling"]["global"]:
            return

        if not conf.instance["general"]["profiling"]["perform"]:
            return

        repeats = conf.instance["general"]["profiling"]["repeats"]

        if not hasattr(obj, "_profiling_dict"):
            obj._profiling_dict = {}

        start = time.time()
        for i in range(repeats):
            result = func(obj, *args, **kwargs)

        time_calc = (time.time() - start) / repeats

        obj._profiling_dict[func.__name__] = time_calc

        return result

    return wrapper


class CachedProperty(object):
    """
    A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.

    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


cached_property = CachedProperty