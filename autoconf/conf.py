import os
from pathlib import Path

from autoconf.json_prior.config import JSONPriorConfig
from autoconf.named import NamedConfig, AbstractConfig


def get_matplotlib_backend():
    try:
        return instance["visualize_general"]["general"]["backend"]
    except KeyError:
        return "default"


class RecursiveConfig(AbstractConfig):
    def items(self):
        items = list()
        for path in os.listdir(self.path):
            path = path.split(".")[0]
            items.append((
                path,
                self[path]
            ))
        return items

    def __init__(self, path):
        self.path = Path(path)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.path}>"

    def _getitem(self, item):
        item_path = self.path / f"{item}"
        file_path = f"{item_path}.ini"
        if os.path.isfile(file_path):
            return NamedConfig(
                file_path
            )
        if os.path.isdir(item_path):
            return RecursiveConfig(
                item_path
            )
        raise KeyError(
            f"No configuration found for {item} at path {self.path}"
        )


class ConfigWrapper(AbstractConfig):
    def __init__(self, configs):
        self.configs = configs

    def __applicable(self, item):
        __applicable = list()
        for config in self.configs:
            try:
                __applicable.append(config[item])
            except KeyError:
                pass
        return __applicable

    def items(self):
        item_dict = {}
        for config in self.configs:
            for key, value in config.items():
                item_dict[key] = value
        return list(item_dict.items())

    def _getitem(self, item):
        configs = self.__applicable(item)
        if len(configs) == 0:
            paths = '\n'.join(map(str, self.configs))
            raise KeyError(
                f"No configuration for {item} in {paths}"
            )
        for config in configs:
            if not isinstance(
                    config, AbstractConfig
            ):
                return config
        return ConfigWrapper(configs)


class Config(ConfigWrapper):
    def __init__(self, *config_paths, output_path="output"):
        super().__init__(list(map(
            RecursiveConfig,
            config_paths
        )))
        self._prior_config = None
        self.output_path = output_path

    @property
    def path(self):
        return self.configs[0].path

    @property
    def prior_config(self):
        if self._prior_config is None:
            self._prior_config = JSONPriorConfig.from_directory(
                self.path / "json_priors"
            )
        return self._prior_config

    def push(self, new_path, output_path=None):
        self.configs = [RecursiveConfig(
            new_path
        )] + self.configs
        self.output_path = output_path or self.output_path

    @classmethod
    def for_directory(cls, directory):
        directory_path = Path(directory)
        return Config(
            directory_path / "config",
            output_path=directory_path / "output"
        )


current_directory = os.getcwd()

default = Config(
    f"{current_directory}/config",
    f"{current_directory}/output/"
)

instance = default
