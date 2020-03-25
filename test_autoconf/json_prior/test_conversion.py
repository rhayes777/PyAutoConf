import os
from pathlib import Path

import pytest

from autoconf.json_prior import converter as c


@pytest.fixture(name="prior_directory")
def make_prior_directory():
    return str(Path(__file__).parent.parent / "test_files" / "config" / "priors")


@pytest.fixture(name="converter")
def make_converter(prior_directory):
    return c.Converter(prior_directory)


@pytest.fixture(name="prior_json")
def make_prior_json(converter):
    return converter.dict


def test_modules(converter):
    assert converter.modules == ["mock", "test_model_mapper"]


@pytest.fixture(name="mock_json")
def make_mock_json(prior_json):
    return prior_json["mock"]


class TestPrior:
    def test_uniform(self, mock_json):
        uniform_dict = mock_json["EllipticalSersic"]["intensity"]
        assert uniform_dict == {
            "type": "Uniform",
            "lower_limit": 0.0,
            "upper_limit": 1.0,
            'gaussian_limits': {'lower': 0.0, 'upper': 10.0},
        }

    def test_gaussian(self, mock_json):
        gaussian_dict = mock_json["AbstractEllipticalSersic"]["intensity"]
        assert gaussian_dict == {
            "type": "Gaussian",
            "mean": 0.0,
            "sigma": 0.5,
            "lower_limit": "-inf",
            "upper_limit": "inf",
        }

    @pytest.mark.parametrize(
        "key, type_string",
        [("grid", "Deferred"), ("nothing", "Constant"), ("constant", "Constant")],
    )
    def test_constants(self, mock_json, key, type_string):
        assert mock_json["Tracer"][key]["type"] == type_string


def test_limit(mock_json):
    limit_dict = mock_json["MockClassNLOx4"]["four"]["gaussian_limits"]
    assert limit_dict["lower"] == -120
    assert limit_dict["upper"] == 120


class TestWidth:
    def test_relative(self, mock_json):
        assert mock_json["RelativeWidth"]["one"]["width_modifier"] == {
            "type": "Relative",
            "value": 0.1,
        }

    def test_absolute(self, mock_json):
        assert mock_json["EllipticalExponential"]["intensity"]["width_modifier"] == {
            "type": "Absolute",
            "value": 1.0,
        }
