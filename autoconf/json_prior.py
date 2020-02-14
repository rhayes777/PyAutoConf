def path_for_class(cls):
    return f"{cls.__module__}.{cls.__name__}"


class JSONPriorConfig:
    def __init__(self, config_dict):
        self.config_dict = config_dict

    def __call__(self, config_path):
        return self.config_dict[
            config_path
        ]
