import inspect
import json
import logging

import numpy as np
from pathlib import Path
from typing import Union, Callable

from autoconf.class_path import get_class_path, get_class

logger = logging.getLogger(__name__)


np_type_map = {
    "bool": "bool_",
}


def nd_array_as_dict(obj: np.ndarray) -> dict:
    """
    Converts a numpy array to a dictionary representation.
    """
    np_type = str(obj.dtype)
    return {
        "type": "ndarray",
        "array": obj.tolist(),
        "dtype": np_type_map.get(np_type, np_type),
    }


def nd_array_from_dict(nd_array_dict: dict, **_) -> np.ndarray:
    """
    Converts a dictionary representation back to a numpy array.
    """
    return np.array(nd_array_dict["array"], dtype=getattr(np, nd_array_dict["dtype"]))


def to_dict(obj):
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj

    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except TypeError as e:
            logger.debug(e)

    if isinstance(obj, np.ndarray):
        try:
            return nd_array_as_dict(obj)
        except Exception as e:
            logger.info(e)

    if inspect.isclass(obj):
        return {
            "type": "type",
            "class_path": get_class_path(obj),
        }

    if isinstance(obj, list):
        return {"type": "list", "values": list(map(to_dict, obj))}
    if isinstance(obj, dict):
        return {
            "type": "dict",
            "arguments": {key: to_dict(value) for key, value in obj.items()},
        }
    if obj.__class__.__name__ == "method":
        return to_dict(obj())
    if obj.__class__.__module__ == "builtins":
        return obj

    if inspect.isclass(type(obj)):
        return instance_as_dict(obj)

    return obj


def instance_as_dict(obj):
    arguments = set(inspect.getfullargspec(obj.__init__).args[1:])
    try:
        arguments |= set(obj.__identifier_fields__)
    except (AttributeError, TypeError):
        pass
    argument_dict = {
        arg: getattr(obj, arg)
        for arg in arguments
        if hasattr(obj, arg)
        and not inspect.ismethod(
            getattr(obj, arg),
        )
    }

    return {
        "type": "instance",
        "class_path": get_class_path(obj.__class__),
        "arguments": {key: to_dict(value) for key, value in argument_dict.items()},
    }


__parsers = {
    "ndarray": nd_array_from_dict,
}


def register_parser(type_: str, parser: Callable[[dict], object]):
    """
    Register a parser for a given type.

    This parser will be used to instantiate objects of the given type from a
    dictionary representation.

    Parameters
    ----------
    type_
        The type of the object to be parsed. This is a string uniquely
        identifying the type.
    parser
        A function which takes a dictionary representation of an object and
        returns an instance of the object.
    """
    __parsers[type_] = parser


def from_dict(dictionary, **kwargs):
    """
    Instantiate an instance of a class from its dictionary representation.

    Parameters
    ----------
    dictionary
        An object which may be a dictionary representation of an object.

        This may contain the following keys:
        type: str
            The type of the object. This may be a built-in type, a numpy array,
            a list, a dictionary, a class, or an instance of a class.

            If a parser has been registered for the given type that parser will
            be used to instantiate the object.
        class_path: str
            The path to the class of the object. This is used to instantiate
            the object if it is not a built-in type.
        arguments: dict
            A dictionary of arguments to pass to the class constructor.

    Returns
    -------
    An object that was represented by the dictionary.
    """
    if isinstance(dictionary, (int, float, str, bool, type(None))):
        return dictionary

    if isinstance(dictionary, list):
        return list(map(from_dict, dictionary))

    if isinstance(dictionary, tuple):
        return tuple(map(from_dict, dictionary))

    try:
        type_ = dictionary["type"]
    except KeyError:
        logger.debug("No type field in dictionary")
        return dictionary
    except TypeError as e:
        logger.debug(e)
        return None

    if type_ in __parsers:
        return __parsers[type_](dictionary, **kwargs)

    if type_ == "list":
        return list(map(from_dict, dictionary["values"]))
    if type_ == "dict":
        return {key: from_dict(value, **kwargs) for key, value in dictionary.items()}

    if type_ == "type":
        return get_class(dictionary["class_path"])

    cls = get_class(dictionary["class_path"])

    if cls is np.ndarray:
        return nd_array_from_dict(dictionary)
    if hasattr(cls, "from_dict"):
        return cls.from_dict(dictionary, **kwargs)

    # noinspection PyArgumentList
    return cls(
        **{
            name: from_dict(value, **kwargs)
            for name, value in dictionary["arguments"].items()
        }
    )


def from_json(file_path: str):
    """
    Load the dictable object to a .json file, whereby all attributes are converted from the .json file's dictionary
    representation to create the instance of the object

    A json file of the instance can be created from the .json file via the `output_to_json` method.

    Parameters
    ----------
    file_path
        The path to the .json file that the dictionary representation of the object is loaded from.
    """
    with open(file_path, "r+") as f:
        cls_dict = json.load(f)

    return from_dict(cls_dict)


def output_to_json(obj, file_path: Union[Path, str]):
    """
    Output the dictable object to a .json file, whereby all attributes are converted to a dictionary representation
    first.

    An instance of the object can be created from the .json file via the `from_json` method.

    Parameters
    ----------
    file_path
        The path to the .json file that the dictionary representation of the object is written too.
    """
    with open(file_path, "w+") as f:
        json.dump(to_dict(obj), f, indent=4)
