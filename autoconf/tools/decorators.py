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