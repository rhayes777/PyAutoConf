import shutil

import json
import os
from pathlib import Path

import pytest

from autoconf.json_prior import generate as g

directory = Path(__file__).parent
package_directory = directory / "source_code"
module_path = package_directory / "module.py"
output_directory = Path(__file__).parent / "output"


@pytest.fixture(name="prior_json")
def make_prior_json():
    return {
        "MyClass": {
            "simple": {
                "gaussian_limits": {"lower": 0.0, "upper": 1.0},
                "lower_limit": 0.0,
                "type": "Uniform",
                "upper_limit": 1.0,
                "width_modifier": {"type": "Absolute", "value": 0.2},
            },
            "tup_0": {
                "gaussian_limits": {"lower": 0.0, "upper": 1.0},
                "lower_limit": 0.0,
                "type": "Uniform",
                "upper_limit": 1.0,
                "width_modifier": {"type": "Absolute", "value": 0.2},
            },
            "tup_1": {
                "gaussian_limits": {"lower": 0.0, "upper": 1.0},
                "lower_limit": 0.0,
                "type": "Uniform",
                "upper_limit": 1.0,
                "width_modifier": {"type": "Absolute", "value": 0.2},
            },
        }
    }


@pytest.fixture(autouse=True)
def cleanup():
    yield
    try:
        shutil.rmtree(output_directory)
    except FileNotFoundError:
        pass


def test_generate_for_file(prior_json):
    result = g.for_file(module_path)
    assert result == prior_json


def test_generate(prior_json):
    g.generate(package_directory, output_directory=output_directory)

    with open(output_directory / "module.json") as f:
        assert json.load(f) == prior_json
