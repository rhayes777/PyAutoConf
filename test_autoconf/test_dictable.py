import json

import numpy as np
import pytest

from autoconf.dictable import to_dict, from_dict, register_parser


@pytest.fixture(name="array_dict")
def make_array_dict():
    return {"array": [1.0], "dtype": "float64", "type": "ndarray"}


@pytest.fixture(name="array")
def make_array():
    return np.array([1.0])


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
