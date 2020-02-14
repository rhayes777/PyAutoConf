from autoconf.exc import PriorException


def path_for_class(cls):
    return f"{cls.__module__}.{cls.__name__}".split(".")


class JSONPriorConfig:
    def __init__(self, config_dict):
        self.config_dict = config_dict

    def __call__(self, config_path):
        original_config_path = config_path
        after = []
        config_dict = self.config_dict
        while len(config_path) > 0:
            key = ".".join(config_path)
            if key in config_dict:
                config_dict = config_dict[
                    key
                ]
                if len(after) == 0:
                    return config_dict
                config_path = after
                after = []
            else:
                after = config_path[-1:] + after
                config_path = config_path[:-1]
        raise PriorException(
            f"No configuration was found for the path {original_config_path}"
        )
