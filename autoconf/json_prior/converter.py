import json
from glob import glob


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
    def modules(self):
        paths = glob(f"{self.default_directory}/*.ini")
        return [
            path.replace(
                ".ini", ""
            ).split("/")[-1]
            for path
            in paths
        ]

    def convert(self):
        return {
            module: {}
            for module
            in self.modules
        }


def convert(directory):
    with open(f"{directory}.json", "w+") as f:
        json.dump(
            Converter(
                directory
            ).convert(),
            f
        )
