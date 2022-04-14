import numpy as np
import pytest

from autoconf.dictable import as_dict, Dictable


@pytest.fixture(
    name="array_dict"
)
def make_array_dict():
    return {
        'type': 'numpy.ndarray',
        'array': [1.0],
        'dtype': 'float64'
    }


@pytest.fixture(
    name="array"
)
def make_array():
    return np.array([1.0])


def test_array_as_dict(
        array_dict,
        array
):
    assert as_dict(array) == array_dict


def test_from_dict(
        array_dict,
        array
):
    assert Dictable.from_dict(
        array_dict
    ) == array
