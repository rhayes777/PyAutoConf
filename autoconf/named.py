import configparser
from abc import abstractmethod, ABC


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
        raise KeyError(
            f"No configuration found for {cls.__name__}"
        )


class SectionConfig(AbstractConfig):
    def __init__(self, path, section):
        self.path = path
        self.section = section
        self.parser = configparser.ConfigParser()
        self.parser.read(path)

    def keys(self):
        return [item[0] for item in self.parser.items(self.section)]

    def _getitem(self, item):
        try:
            result = self.parser.get(
                self.section,
                item
            )
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
            raise KeyError(
                f"No configuration found for {item} at path {self.path}"
            )


class NamedConfig(AbstractConfig):
    """Parses generic config"""

    def __init__(self, config_path):
        """
        Parameters
        ----------
        config_path: String
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
            item,
        )


def family(current_class):
    yield current_class
    for next_class in current_class.__bases__:
        for val in family(next_class):
            yield val
