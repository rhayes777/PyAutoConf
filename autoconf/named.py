import configparser
from abc import abstractmethod, ABC
from copy import deepcopy


class AbstractConfig(ABC):
    @abstractmethod
    def __getitem__(self, item):
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

    def __getitem__(self, item):
        try:
            result = self.parser.get(
                self.section,
                item
            )
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise KeyError(
                f"No configuration found for {item} at path {self.path}"
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

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, v if k == "parser" else deepcopy(v, memo))
        return result

    def __getitem__(self, item):
        return SectionConfig(
            self.path,
            item
        )

    def __eq__(self, other):
        return isinstance(other, NamedConfig) and self.path == other.path

    def get(self, section_name, attribute_name, attribute_type=str):
        """

        Parameters
        ----------
        section_name
        attribute_type: type
            The type to which the value should be cast
        attribute_name: String
            The analysis_path of the attribute

        Returns
        -------
        prior_array: []
            An arrays describing a prior
        """
        try:
            string_value = self.parser.get(section_name, attribute_name)
        except configparser.NoSectionError:
            raise configparser.NoSectionError(
                "Could not find section {} in config at path {}".format(
                    section_name, self.path
                )
            )
        except configparser.NoOptionError as e:
            raise configparser.NoOptionError(
                "could not find option {} in section {} of config at path {}".format(
                    attribute_name, section_name, self.path
                ),
                e.section,
            )
        if string_value == "None":
            return None
        if attribute_type is bool:
            return string_value == "True"
        return attribute_type(string_value)

    def has(self, section_name, attribute_name):
        """
        Parameters
        ----------
        section_name
        attribute_name: String
            The analysis_path of the attribute

        Returns
        -------
        has_prior: bool
            True iff a prior exists for the module, class and attribute
        """
        return self.parser.has_option(section_name, attribute_name)


def family(current_class):
    yield current_class
    for next_class in current_class.__bases__:
        for val in family(next_class):
            yield val
