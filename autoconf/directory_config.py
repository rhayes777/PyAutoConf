import configparser
import os
from abc import abstractmethod, ABC
from pathlib import Path

import yaml

from autoconf import exc


class AbstractConfig(ABC):
    @abstractmethod
    def _getitem(self, item):
        pass

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.items()[item]
        return self._getitem(item)

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def __len__(self):
        return len(self.items())

    @abstractmethod
    def keys(self):
        pass

    def family(self, cls):
        for cls in family(cls):
            key = cls.__name__
            try:
                return self[key]
            except (KeyError, configparser.NoOptionError):
                pass
        raise KeyError(f"No configuration found for {cls.__name__}")

    def dict(self):
        d = {}
        for key in self.keys():
            value = self[key]
            if isinstance(value, AbstractConfig):
                value = value.dict()
            d[key] = value
        return d


class DictConfig(AbstractConfig):
    def keys(self):
        return self.d.keys()

    def __init__(self, d):
        self.d = d

    def __getitem__(self, item):
        value = self.d[item]
        if isinstance(value, dict):
            return DictConfig(value)
        return value

    def _getitem(self, item):
        return self[item]

    def items(self):
        for key in self.d:
            yield key, self[key]


class YAMLConfig(AbstractConfig):
    def __init__(self, path):
        with open(path) as f:
            self._dict = yaml.safe_load(f)

    def _getitem(self, item):
        value = self._dict[item]
        if isinstance(value, dict):
            return DictConfig(value)
        return value

    def keys(self):
        return self._dict.keys()


class SectionConfig(AbstractConfig):
    def __init__(self, path, parser, section):
        self.path = path
        self.section = section
        self.parser = parser

    def keys(self):
        with open(self.path) as f:
            string = f.read()

        lines = string.split("\n")
        is_section = False
        for line in lines:
            if line == f"[{self.section}]":
                is_section = True
                continue
            if line.startswith("["):
                is_section = False
                continue
            if is_section and "=" in line:
                yield line.split("=")[0]

    def _getitem(self, item):
        try:
            result = self.parser.get(self.section, item)
            if result.lower() == "true":
                return True
            if result.lower() == "false":
                return False
            if result.lower() in ("none", "null"):
                return None
            if result.isdigit():
                return int(result)
            try:
                return float(result)
            except ValueError:
                return result
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise KeyError(f"No configuration found for {item} at path {self.path}")


class NamedConfig(AbstractConfig):
    def __init__(self, config_path):
        """
        Parses generic config

        Parameters
        ----------
        config_path
            The path to the config file
        """
        self.path = config_path
        self.parser = configparser.ConfigParser()
        self.parser.read(self.path)

    def keys(self):
        return self.parser.sections()

    def _getitem(self, item):
        return SectionConfig(
            self.path,
            self.parser,
            item,
        )


class RecursiveConfig(AbstractConfig):
    def keys(self):
        try:
            return [
                path.split(".")[0]
                for path in os.listdir(self.path)
                if all(
                    [
                        path != "priors",
                        len(path.split(".")[0]) != 0,
                        os.path.isdir(f"{self.path}/{path}")
                        or path.endswith(".ini")
                        or path.endswith(".yaml")
                        or path.endswith(".yml"),
                    ]
                )
            ]
        except FileNotFoundError as e:
            raise KeyError(f"No configuration found at {self.path}") from e

    def __init__(self, path):
        self.path = Path(path)

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.path}>"

    def _getitem(self, item):
        item_path = self.path / f"{item}"
        file_path = f"{item_path}.ini"
        if os.path.isfile(file_path):
            return NamedConfig(file_path)
        yml_path = item_path.with_suffix(".yml")
        if yml_path.exists():
            return YAMLConfig(yml_path)
        yaml_path = item_path.with_suffix(".yaml")
        if yaml_path.exists():
            return YAMLConfig(yaml_path)
        if os.path.isdir(item_path):
            return RecursiveConfig(item_path)
        raise KeyError(f"No configuration found for {item} at path {self.path}")


class PriorConfigWrapper:
    def __init__(self, prior_configs):
        self.prior_configs = prior_configs

    def for_class_and_suffix_path(self, cls, path):
        for config in self.prior_configs:
            try:
                return config.for_class_and_suffix_path(cls, path)
            except KeyError:
                pass
        directories = " ".join(str(config.directory) for config in self.prior_configs)

        print()

        raise exc.ConfigException(
            f"No prior config found for class: \n\n"
            f"{cls.__name__} \n\n"
            f"For parameter name and path: \n\n "
            f"{'.'.join(path)} \n\n "
            f"In any of the following directories:\n\n"
            f"{directories}\n\n"
            f"Either add configuration for the parameter or a type annotation for a class with valid configuration.\n\n"
            f"The following readthedocs page explains prior configuration files in PyAutoFit and will help you fix "
            f"the error https://pyautofit.readthedocs.io/en/latest/general/adding_a_model_component.html"
        )


def family(current_class):
    yield current_class
    for next_class in current_class.__bases__:
        for val in family(next_class):
            yield val
