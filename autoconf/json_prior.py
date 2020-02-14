import json
from typing import List, Iterable

from autoconf.exc import PriorException


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
    def __init__(self, config_dict: dict):
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
        self.config_dict = config_dict

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
                json.load(f)
            )

    def __str__(self):
        return json.dumps(self.config_dict)

    def __call__(self, config_path: Iterable[str]):
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
