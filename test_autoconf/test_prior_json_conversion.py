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
        "test_model_mapper",
        "test_prior_model"
    ]


def test_geometry_profiles(prior_json):
    assert "*.geometry_profiles" in prior_json
    profiles_json = prior_json["*.geometry_profiles"]
    assert "GeometryProfile" in profiles_json
    assert "centre_0" in profiles_json["GeometryProfile"]
