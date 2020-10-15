import os
from pathlib import Path

from autoconf.directory_config import ConfigWrapper, RecursiveConfig
from autoconf.json_prior.config import JSONPriorConfig


def get_matplotlib_backend():
    try:
        return instance["visualize_general"]["general"]["backend"]
    except KeyError:
        return "default"


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
                self.path / "priors"
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
