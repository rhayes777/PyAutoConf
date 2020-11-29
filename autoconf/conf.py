import logging
import os
from pathlib import Path
from typing import Optional

from autoconf.directory_config import RecursiveConfig, PriorConfigWrapper, AbstractConfig, family
from autoconf.json_prior.config import JSONPriorConfig

logger = logging.getLogger(__name__)


def get_matplotlib_backend():
    try:
        return instance["visualize"]["general"]["general"]["backend"]
    except KeyError:
        return "default"


class DictWrapper:
    def __init__(self, paths):
        self._dict = dict()
        self.paths = paths

    def __contains__(self, item):
        return item in self._dict

    def items(self):
        return self._dict.items()

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = key.lower()
        self._dict[key] = value

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.lower()
        try:
            return self._dict[key]
        except KeyError:
            raise KeyError(
                f"key {key} not found in paths {self.paths_string}"
            )

    @property
    def paths_string(self):
        return "\n".join(
            map(str, self.paths)
        )

    def __repr__(self):
        return repr(self._dict)

    def family(self, cls):
        for item in family(cls):
            try:
                return self[item]
            except KeyError:
                pass
        raise KeyError(
            f"config for {cls} or its parents not found in paths {self.paths_string}"
        )


class Config:
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
        self._configs = list()
        self._dict = DictWrapper(
            self.paths
        )

        self.configs = list(map(
            RecursiveConfig,
            config_paths
        ))

        self.output_path = output_path

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, configs):
        self._configs = configs

        def recurse_config(
                config,
                d
        ):
            try:
                for key, value in config.items():
                    if isinstance(
                            value,
                            AbstractConfig
                    ):
                        if key not in d:
                            d[key] = DictWrapper(
                                self.paths
                            )
                        recurse_config(
                            value,
                            d=d[key]
                        )
                    else:
                        d[key] = value
            except KeyError as e:
                logger.debug(e)

        for config_ in reversed(configs):
            recurse_config(config_, self._dict)

    def __getitem__(self, item):
        return self._dict[item]

    @property
    def paths(self):
        return [
            config.path
            for config
            in self._configs
        ]

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
        self.output_path = output_path or self.output_path

        if self.configs[0] == new_path or (
                keep_first and len(self.configs) > 1 and self.configs[1] == new_path
        ):
            return
        new_config = RecursiveConfig(
            new_path
        )

        configs = list(filter(
            lambda config: config != new_config,
            self.configs
        ))
        if keep_first:
            self.configs = configs[:1] + [new_config] + configs[1:]
        else:
            self.configs = [new_config] + configs

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