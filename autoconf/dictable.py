import inspect
import json
import logging

import numpy as np
from pathlib import Path
from typing import Union

from autoconf.class_path import get_class_path, get_class

logger = logging.getLogger(__name__)


def nd_array_as_dict(obj: np.ndarray) -> dict:
    """
    Converts a numpy array to a dictionary representation.
    """
    return {
        "type": "ndarray",
        "array": obj.tolist(),
        "dtype": str(obj.dtype),
    }


def nd_array_from_dict(nd_array_dict: dict) -> np.ndarray:
    """
    Converts a dictionary representation back to a numpy array.
    """
    return np.array(nd_array_dict["array"], dtype=getattr(np, nd_array_dict["dtype"]))


def as_dict(obj):
    if hasattr(obj, "dict"):
        return obj.dict()

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
        return {"type": "list", "values": list(map(as_dict, obj))}
    if isinstance(obj, dict):
        return {
            "type": "dict",
            "arguments": {key: as_dict(value) for key, value in obj.items()},
        }
    if obj.__class__.__module__ == "builtins":
        return obj

    return instance_as_dict(obj)


def instance_as_dict(obj):
    argument_dict = {
        arg: getattr(obj, arg) for arg in inspect.getfullargspec(obj.__init__).args[1:]
    }

    return {
        "type": "instance",
        "class_path": get_class_path(obj.__class__),
        "arguments": {key: as_dict(value) for key, value in argument_dict.items()},
    }


def from_dict(cls_dict):
    """
    Instantiate an instance of a class from its dictionary representation.

    Parameters
    ----------
    cls_dict
        A dictionary representation of the instance comprising a type
        field which contains the entire class path by which the type
        can be imported and constructor arguments.

    Returns
    -------
    An instance of the geometry profile specified by the type field in
    the cls_dict
    """
    if isinstance(cls_dict, list):
        return list(map(from_dict, cls_dict))
    if not isinstance(cls_dict, dict):
        return cls_dict
    type_ = cls_dict["type"]

    if type_ == "ndarray":
        return nd_array_from_dict(cls_dict)

    if type_ == "list":
        return list(map(from_dict, cls_dict["values"]))
    if type_ == "dict":
        return {key: from_dict(value) for key, value in cls_dict.items()}

    if type_ == "type":
        return get_class(cls_dict["class_path"])

    cls = get_class(cls_dict["class_path"])

    if cls is np.ndarray:
        return nd_array_from_dict(cls_dict)

    # noinspection PyArgumentList
    return cls(
        **{name: from_dict(value) for name, value in cls_dict["arguments"].items()}
    )


def from_json(file_path: str) -> "Dictable":
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
        json.dump(as_dict(obj), f, indent=4)
