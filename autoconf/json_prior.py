import json
from typing import List

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
        self.obj = config_dict

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
        return json.dumps(self.obj)

    def _matching_key(self, item):
        key = ".".join(item)
        if key in self.obj:
            return key
        for i in range(1, len(item)):
            key = f"*.{'.'.join(item[:-i])}"
            if key in self.obj:
                return key
        raise KeyError(f"No such item {item}")

    def __getitem__(self, item):
        return JSONPriorConfig(
            self.obj[self._matching_key(item)]
        )

    def __contains__(self, item):
        try:
            _ = self._matching_key(item)
            return True
        except KeyError:
            return False

    @property
    def wildcards(self):
        def get_wild_cards(obj):
            wild_cards = dict()
            if not isinstance(obj, dict):
                return wild_cards
            for key, value in obj.items():
                if key.startswith("*."):
                    wild_cards[key] = value
                wild_cards = {
                    **wild_cards,
                    **get_wild_cards(
                        value
                    )
                }
            return wild_cards

        return get_wild_cards(
            self.obj
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
        wild_path = config_path
        while len(wild_path) > 0:
            wild_card_key = f"*.{'.'.join(wild_path)}"
            for key, value in self.wildcards.items():
                if wild_card_key.startswith(key):
                    try:
                        return JSONPriorConfig(
                            {
                                key[2:]: value
                            }
                        )(wild_card_key[2:].split("."))
                    except PriorException:
                        pass
            wild_path = wild_path[1:]

        current_path = config_path
        after = []
        while len(current_path) > 0:
            if current_path in self:
                config = self[
                    current_path
                ]
                if len(after) == 0:
                    return config.obj
                return config(after)

            after = current_path[-1:] + after
            current_path = current_path[:-1]
        raise PriorException(
            f"No configuration was found for the path {config_path}"
        )
