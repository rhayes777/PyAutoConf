from functools import wraps
from autoconf.conf import instance


def conditional_output(func):
    @wraps(func)
    def wrapper(self, name, *args, **kwargs):
        if instance["output"][name]:
            return func(self, name, *args, **kwargs)

    return wrapper
