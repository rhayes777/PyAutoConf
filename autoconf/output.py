from functools import wraps
from autoconf.conf import instance


def should_output(name):
    output_config = instance["output"]
    try:
        return output_config[name]
    except KeyError:
        return output_config["default"]


def conditional_output(func):
    @wraps(func)
    def wrapper(self, name, *args, **kwargs):
        if should_output(name):
            return func(self, name, *args, **kwargs)

    return wrapper
