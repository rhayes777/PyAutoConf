import os
from pathlib import Path

from autoconf.directory_config import ConfigWrapper, RecursiveConfig, PriorConfigWrapper
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
        self.output_path = output_path

    @property
    def path(self):
        return self.configs[0].path

    @property
    def prior_config(self):
        return PriorConfigWrapper([
            JSONPriorConfig.from_directory(
                path / "priors"
            )
            for path in self.paths
        ])

    def push(
            self,
            new_path,
            output_path=None,
            keep_first=False
    ):
        new_config = RecursiveConfig(
            new_path
        )
        if keep_first:
            self.configs = self.configs[:1] + [new_config] + self.configs[1:]
        else:
            self.configs = [new_config] + self.configs
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
