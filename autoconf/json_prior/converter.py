import json
from configparser import ConfigParser
from glob import glob


class Prior:
    def __init__(
            self,
            cls,
            name
    ):
        print(name)
        self.name = name
        self.cls = cls

    @property
    def default_string(self):
        return self.cls.default_section[self.name]

    @property
    def default_array(self):
        return self.default_string.split(",")

    @property
    def limit_string(self):
        return self.cls.limit_section[self.name]

    @property
    def limit_array(self):
        return self.limit_string.split(",")

    @property
    def type_character(self):
        return self.default_array[0]

    @property
    def type_string(self):
        if self.type_character == "u":
            return "Uniform"

    @property
    def lower_limit(self):
        return float(self.default_array[1])

    @property
    def upper_limit(self):
        try:
            return float(self.default_array[2])
        except IndexError:
            pass

    @property
    def dict(self):
        prior_dict = {
            "type": self.type_string
        }
        if self.type_character == "d":
            return prior_dict
        if self.type_string == "n":
            return {
                **prior_dict,
                "value": None
            }
        if self.type_character == "c":
            value = self.default_array[1]
            try:
                value = float(value)
            except ValueError:
                pass
            return {
                **prior_dict,
                "value": value
            }
        prior_dict = {
            **prior_dict,
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit

        }
        if self.type_character in ("u", "l"):
            return prior_dict
        if self.type_character == "g":
            lower_limit = float("-inf")
            upper_limit = float("-inf")
            try:
                lower_limit = float(self.limit_array[0])
                upper_limit = float(self.limit_array[1])
            except KeyError:
                pass
            return {
                **prior_dict,
                "mean": float(self.default_array[1]),
                "sigma": float(self.default_array[2]),
                "lower_limit": lower_limit,
                "upper_limit": upper_limit
            }
        raise AssertionError(
            f"Unrecognised prior type {self.type_character}"
        )


class Class:
    def __init__(self, module, name):
        print(name)
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
    def limit_section(self):
        return self.module.limit[self.name]

    @property
    def dict(self):
        return {
            prior.name: prior.dict
            for prior
            in self.priors
        }


class Module:
    def __init__(self, converter, name):
        print(name)
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
