import os
from pathlib import Path

from autoconf.directory_config import ConfigWrapper, RecursiveConfig, PriorConfigWrapper
from autoconf.json_prior.config import JSONPriorConfig


def get_matplotlib_backend():
    try:
        return instance["visualize"]["general"]["general"]["backend"]
    except KeyError:
        return "default"


class Config(ConfigWrapper):
    def __init__(self, *config_paths, output_path="output"):
        """
        Singleton to manage configuration.

        Configuration is loaded using the __getitem__ syntax where the key entered
        can refer to a directory, file, section or item.

        Configuration is first attempted to be loaded from the directory indicated by the first
        config_path. If no configuration is found the second directory is searched and so on.
        This allows a default configuration to be defined with additional configuration overriding
        it.

        Parameters
        ----------
        config_paths
            Indicate directories where configuration is defined, in the order of priority with
            configuration in the first config_path overriding configuration in later config
            paths
        output_path
            The path where data should be saved.
        """
        super().__init__(list(map(
            RecursiveConfig,
            config_paths
        )))
        self.output_path = output_path

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

    def register(self, file):
        self.push(
            Path(file).parent / "config",
            keep_first=True
        )


current_directory = os.getcwd()

default = Config(
    f"{current_directory}/config",
    f"{current_directory}/output/"
)

instance = default
