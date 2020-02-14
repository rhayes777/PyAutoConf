import json
import os
from pathlib import Path

import pytest
from autoconf.json_prior import converter


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
    name="prior_json",
    autouse=True
)
def make_prior_json(prior_directory, prior_filename):
    converter.convert(prior_directory)
    with open(prior_filename) as f:
        return json.load(f)


def test_convert(prior_filename):
    assert os.path.exists(prior_filename)


def test_geometry_profiles(prior_json):
    assert "geometry_profiles" in prior_json
