import os
from pathlib import Path
from typing import Optional

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
    def prior_config(self) -> PriorConfigWrapper:
        """
        Configuration for priors. This indicates, for example, the mean and the width of priors
        for the attributes of given classes.
        """
        return PriorConfigWrapper([
            JSONPriorConfig.from_directory(
                path / "priors"
            )
            for path in self.paths
        ])

    def push(
            self,
            new_path: str,
            output_path: Optional[str] = None,
            keep_first: bool = False
    ):
        """
        Push a new configuration path. This overrides the existing config
        paths, with existing configs being used as a backup when a value
        cannot be found in an overriding config.

        Parameters
        ----------
        new_path
            A path to config directory
        output_path
            The path at which data should be output. If this is None then it remains
            unchanged
        keep_first
            If True the current priority configuration mains such.
        """
        new_config = RecursiveConfig(
            new_path
        )
        if keep_first:
            self.configs = self.configs[:1] + [new_config] + self.configs[1:]
        else:
            self.configs = [new_config] + self.configs
        self.output_path = output_path or self.output_path

    def register(self, file: str):
        """
        Add defaults for a given project

        Parameters
        ----------
        file
            The path to the project's __init__
        """
        self.push(
            Path(file).parent / "config",
            keep_first=True
        )


current_directory = Path(os.getcwd())

default = Config(
    current_directory / "config",
    current_directory / "output/"
)

instance = default
