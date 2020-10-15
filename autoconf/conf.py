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
    def __init__(self, path, default_configs=tuple()):
        super().__init__(default_configs)
        self.path = Path(path)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.path}>"

    def __getitem__(self, item):
        item_path = self.path / f"{item}"
        file_path = f"{item_path}.ini"
        default_configs = self._default_configs_for_item(
            item
        )
        if os.path.isfile(file_path):
            return NamedConfig(
                file_path,
                default_configs=default_configs
            )
        if os.path.isdir(item_path):
            return RecursiveConfig(
                item_path,
                default_configs=default_configs
            )
        for config in self._default_configs:
            try:
                return config[item]
            except KeyError:
                pass
        raise KeyError(
            f"No configuration found for {item} at path {self.path}"
        )


class Config(RecursiveConfig):
    def __init__(self, config_path, output_path="output", default_config_paths=tuple()):
        super().__init__(config_path)
        self._prior_config = None
        self._default_config_paths = default_config_paths
        self._default_configs = list(map(
            RecursiveConfig,
            default_config_paths
        ))
        self.output_path = output_path

    @property
    def prior_config(self):
        if self._prior_config is None:
            self._prior_config = JSONPriorConfig.from_directory(
                self.path / "json_priors"
            )
        return self._prior_config

    def add_default(self, config_path):
        self._default_configs.append(
            RecursiveConfig(config_path)
        )

    def push(self, new_path):
        return Config(
            new_path,
            output_path=self.output_path,
            default_config_paths=(
                                     self.path,
                                 ) + self._default_config_paths
        )

    @classmethod
    def for_directory(cls, directory):
        directory_path = Path(directory)
        return Config(
            directory_path / "config",
            directory_path / "output"
        )


current_directory = os.getcwd()

default = Config(
    f"{current_directory}/config",
    f"{current_directory}/output/"
)

instance = default
