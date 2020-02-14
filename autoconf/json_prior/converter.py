import json
from glob import glob
from configparser import ConfigParser


class Module:
    def __init__(self, directory, module):
        self.directory = directory
        self.module = module
        self.default = ConfigParser()
        self.default.read(
            f"{self.directory}/default/{self.module}.ini"
        )

    @property
    def classes(self):
        return self.default.sections()

    @property
    def dict(self):
        return {
            cls: {}
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
    def modules(self):
        paths = glob(f"{self.directory}/default/*.ini")
        return [
            path.replace(
                ".ini", ""
            ).split("/")[-1]
            for path
            in paths
        ]

    @property
    def dict(self):
        return {
            f"*.{module}": Module(
                self.directory,
                module
            ).dict
            for module
            in self.modules
        }


def convert(directory):
    with open(f"{directory}.json", "w+") as f:
        json.dump(
            Converter(
                directory
            ).dict,
            f
        )
