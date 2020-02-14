import json
from configparser import ConfigParser
from glob import glob


class Prior:
    def __init__(
            self,
            cls,
            name
    ):
        self.name = name
        self.cls = cls

    @property
    def default_string(self):
        return self.cls.default_section[self.name]

    @property
    def type_string(self):
        return "Uniform"

    @property
    def lower_limit(self):
        return 0.0

    @property
    def upper_limit(self):
        return 1.0

    @property
    def dict(self):
        return {
            "type": self.type_string,
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit
        }


class Class:
    def __init__(self, module, name):
        self.name = name
        self.module = module

    @property
    def priors(self):
        return [
            Prior(
                self,
                name
            )
            for name
            in self.default_section
        ]

    @property
    def default_section(self):
        return self.module.default[self.name]

    @property
    def dict(self):
        return {
            prior.name: prior.dict
            for prior
            in self.priors
        }


class Module:
    def __init__(self, converter, name):
        self.converter = converter
        self.name = name
        self.default = ConfigParser()
        self.default.read(
            f"{self.converter.default_directory}/{self.name}.ini"
        )
        self.limit = ConfigParser()
        self.limit.read(
            f"{self.converter.limit_directory}/{self.name}.ini"
        )
        self.default = ConfigParser()
        self.default.read(
            f"{self.converter.default_directory}/{self.name}.ini"
        )

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        return super().__eq__(other)

    @property
    def classes(self):
        return [
            Class(self, section)
            for section
            in self.default.sections()
        ]

    @property
    def dict(self):
        return {
            cls.name: cls.dict
            for cls
            in self.classes
        }


class Converter:
    def __init__(
            self,
            directory
    ):
        self.directory = directory

    @property
    def default_directory(self):
        return f"{self.directory}/default"

    @property
    def limit_directory(self):
        return f"{self.directory}/limit"

    @property
    def width_directory(self):
        return f"{self.directory}/limit"

    @property
    def modules(self):
        paths = glob(f"{self.directory}/default/*.ini")
        return [
            Module(
                self,
                path.replace(
                    ".ini", ""
                ).split("/")[-1]
            )
            for path
            in paths
        ]

    @property
    def dict(self):
        return {
            f"*.{module.name}": module.dict
            for module
            in self.modules
        }


def convert(directory):
    with open(f"{directory}.json", "w+") as f:
        json.dump(
            Converter(
                directory
            ).dict,
            f,
            sort_keys=True,
            indent=4
        )
