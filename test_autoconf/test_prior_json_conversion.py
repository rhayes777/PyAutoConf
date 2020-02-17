import os
from pathlib import Path

import pytest

from autoconf.json_prior import converter as c


@pytest.fixture(
    name="prior_directory"
)
def make_prior_directory():
    return str(
        Path(__file__).parent / "test_files" / "config" / "priors"
    )


@pytest.fixture(
    name="prior_filename"
)
def make_prior_filename(prior_directory):
    return f"{prior_directory}.json"


@pytest.fixture(
    name="converter"
)
def make_converter(prior_directory):
    return c.Converter(prior_directory)


@pytest.fixture(
    name="prior_json"
)
def make_prior_json(converter):
    return converter.dict


def test_convert(prior_directory, prior_filename):
    c.convert(prior_directory)
    assert os.path.exists(prior_filename)


def test_modules(converter):
    assert converter.modules == [
        "geometry_profiles",
        "mock",
        "test_model_mapper"
    ]


def test_geometry_profiles(prior_json):
    module_json = prior_json["*.geometry_profiles"]
    class_json = module_json["GeometryProfile"]
    assert class_json["centre_0"] == {
        "type": "Uniform",
        "lower_limit": 0.0,
        "upper_limit": 1.0
    }


def test_intensity(prior_json):
    prior_json = prior_json["*.mock"]["AbstractEllipticalSersic"]["intensity"]
    assert prior_json["type"] == "Gaussian"
    assert prior_json["mean"] == 0.0
    assert prior_json["sigma"] == 0.5
    assert prior_json["lower_limit"] == "-inf"
    assert prior_json["upper_limit"] == "inf"

