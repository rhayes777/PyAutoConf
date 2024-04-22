import json

import numpy as np
import pytest
from pathlib import Path

from autoconf.dictable import to_dict, from_dict, register_parser


@pytest.fixture(name="array_dict")
def make_array_dict():
    return {"array": [1.0], "dtype": "float64", "type": "ndarray"}


@pytest.fixture(name="array")
def make_array():
    return np.array([1.0])


class ArrayImpl:
    def __init__(self, array):
        self.array = array

    @property
    def dtype(self):
        return self.array.dtype

    def tolist(self):
        return self.array.tolist()

    def __array__(self):
        return self.array


def test_array_impl(array):
    assert to_dict(ArrayImpl(array)) == to_dict(array)


def test_array_as_dict(array_dict, array):
    assert to_dict(array) == array_dict


def test_from_dict(array_dict, array):
    assert from_dict(array_dict) == array


@pytest.mark.parametrize(
    "array",
    [
        np.array([True]),
        np.array([[1.0]]),
        np.array([[1.0, 2.0], [3.0, 4.0]]),
        np.array([[1, 2], [3, 4]]),
    ],
)
def test_multiple(array):
    assert (from_dict(to_dict(array)) == array).all()


def test_as_json(array):
    assert from_dict(json.loads(json.dumps(to_dict(array)))) == array


def test_with_type_attribute():
    float_dict = {"class_path": "float", "type": "type"}
    assert to_dict(float) == float_dict
    assert from_dict(float_dict) is float


def test_register_parser():
    register_parser("test", lambda x: x["value"])
    assert from_dict({"type": "test", "value": 1}) == 1


def test_no_type():
    assert from_dict({"hi": "there"}) == {"hi": "there"}


def test_serialise_path():
    path = Path("/path/to/file.json")
    path_dict = to_dict(path)
    assert from_dict(path_dict) == path


class Parent:
    def __init__(self, parent_arg):
        self.parent_arg = parent_arg


class Child(Parent):
    def __init__(self, child_arg, **kwargs):
        super().__init__(**kwargs)
        self.child_arg = child_arg


def test_serialise_kwargs():
    child = Child(
        child_arg="child",
        parent_arg="parent",
    )
    child_dict = to_dict(child)
    assert child_dict == {
        "arguments": {
            "child_arg": "child",
            "parent_arg": "parent",
        },
        "class_path": "test_autoconf.test_dictable.Child",
        "type": "instance",
    }
    new_child = from_dict(child_dict)
    assert new_child.child_arg == "child"
    assert new_child.parent_arg == "parent"


class WithOptional:
    def __init__(self, arg: int = 1):
        self.arg = arg


def test_serialise_with_arg():
    assert to_dict(WithOptional()) == {
        "arguments": {"arg": 1},
        "class_path": "test_autoconf.test_dictable.WithOptional",
        "type": "instance",
    }


def test_serialise_without_arg():
    assert to_dict(WithOptional(), filter_args=("arg",)) == {
        "arguments": {},
        "class_path": "test_autoconf.test_dictable.WithOptional",
        "type": "instance",
    }
