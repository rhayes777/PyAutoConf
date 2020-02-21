import inspect
import json
from typing import List, Type, Tuple

from autoconf.exc import PriorException
from autoconf.named import family

default_prior = {
    "type": "Uniform",
    "lower_limit": 0.0,
    "upper_limit": 1.0,
    "width_modifier": {
        "type": "Absolute",
        "value": 0.2
    }
}


def make_config_for_class(cls):
    key = ".".join(path_for_class(cls))
    arguments = inspect.getfullargspec(cls).args[1:]
    config = {
        argument: default_prior
        for argument in arguments
    }
    return key, config


def path_for_class(cls) -> List[str]:
    """
    A list describing the import path for a given class.

    Parameters
    ----------
    cls
        A class with some module path

    Returns
    -------
    A list of modules terminating in the name of a class
    """
    return f"{cls.__module__}.{cls.__name__}".split(".")


class JSONPriorConfig:
    def __init__(
            self,
            config_dict: dict,
            directory=None
    ):
        """
        Parses configuration describing priors associated with classes.

        The path pointing to a class is the same as the path to import it.

        Paths can be strings with '.' as a delimiter.
        {"module.class": config}

        Else they can be a series of dictionary keys.
        {"module": {"class": config}}

        Or any combination thereof.

        Parameters
        ----------
        config_dict
            A dictionary describing the prior configuration for constructor arguments
            of different classes.
        """
        self.obj = config_dict
        self.directory = directory

    @property
    def paths(self):
        return list(self.path_value_map.keys())

    @property
    def path_value_map(self) -> dict:
        """
        A dictionary matching every possible path to the configuration it points to.
        """

        def get_path_values(obj):
            path_values = dict()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    path_values[key] = value
                    for path, path_value in get_path_values(value).items():
                        path_values[f"{key}.{path}"] = path_value

            return path_values

        return get_path_values(
            self.obj
        )

    @property
    def path_value_tuples(self) -> List[Tuple[str, object]]:
        """
        Tuple pairs matching every possible path to the configuration it points to.
        These are ordered by key length with the longest key first.
        """
        return sorted(
            list(self.path_value_map.items()),
            key=lambda item: len(item[0]),
            reverse=True
        )

    @classmethod
    def from_file(cls, filename: str) -> "JSONPriorConfig":
        """
        Load JSONPriorConfiguration from a file.

        Parameters
        ----------
        filename
            The path to a file.

        Returns
        -------
        A configuration instance.
        """
        with open(filename) as f:
            return JSONPriorConfig(
                json.load(f),
                directory=filename
            )

    def __str__(self):
        return json.dumps(self.obj)

    def __getitem__(self, item):
        return JSONPriorConfig(
            self.obj[".".join(item)],
            directory=self.directory
        )

    def __contains__(self, item):
        return ".".join(item) in self.obj

    def for_class_and_suffix_path(
            self,
            cls: Type,
            suffix_path: List[str]
    ):
        """
        Get configuration for a prior.

        If it is just basic configuration then the suffix path is just the
        name of the prior in a list. Width configuration also adds an
        additional "width_modifier" item.

        If configuration is not found for the class then configurations for
        parents of the class are searched.

        Parameters
        ----------
        cls
            The class with which the prior is associated.
        suffix_path
            The path to the prior.

        Returns
        -------
        A configuration dictionary

        Raises
        ------
        PriorException
            If no matching configuration is found.
        """
        for c in family(cls):
            try:
                return self(
                    path_for_class(c) + suffix_path
                )
            except PriorException:
                pass
        raise PriorException(
            f"No configuration was found for the class {cls} and attribute {'.'.join(suffix_path)}"
            + ("" if self.directory is None else f" ({self.directory})")
        )

    def __call__(self, config_path: List[str]):
        """
        Get the config at the end of the config_path.

        The configuration dictionary is traversed until config is found
        at the end, else an exception is thrown.

        Parameters
        ----------
        config_path
            The import path of a package, module, class or class and constructor
            argument name.

        Returns
        -------
        A configuration dictionary or value

        Raises
        ------
        PriorException
            If no configuration is found.
        """
        key = ".".join(config_path)
        for path, value in self.path_value_tuples:
            if key.endswith(path):
                return value
        raise PriorException(
            f"No configuration was found for the path {config_path}"
            + ("" if self.directory is None else f" ({self.directory})")
        )