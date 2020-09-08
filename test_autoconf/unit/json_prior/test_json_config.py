import pytest

import autoconf as aconf
from test_autoconf.mock_real import SphericalProfile


@pytest.fixture(name="geometry_profile_path")
def make_geometry_profile_path():
    return ["test_autoconf", "mock_real", "SphericalProfile"]


def test_path_for_class(geometry_profile_path):
    assert aconf.path_for_class(SphericalProfile) == geometry_profile_path


@pytest.mark.parametrize(
    "config_dict, paths",
    [
        (
            {
                "test_autoconf.mock_real.SphericalProfile": "test",
                "test_autoconf.mock_real.Other": "toast",
            },
            ["test_autoconf.mock_real.SphericalProfile", "test_autoconf.mock_real.Other"],
        ),
        (
            {"test_autoconf.mock_real": {"SphericalProfile": "test", "Other": "toast"}},
            [
                "test_autoconf.mock_real",
                "test_autoconf.mock_real.SphericalProfile",
                "test_autoconf.mock_real.Other",
            ],
        ),
        (
            {"test_autoconf": {"mock_real": {"SphericalProfile": "test", "Other": "toast"}}},
            [
                "test_autoconf",
                "test_autoconf.mock_real",
                "test_autoconf.mock_real.SphericalProfile",
                "test_autoconf.mock_real.Other",
            ],
        ),
        (
            {"test_autoconf": {"mock_real.SphericalProfile": "test", "mock_real.Other": "toast"}},
            [
                "test_autoconf",
                "test_autoconf.mock_real.SphericalProfile",
                "test_autoconf.mock_real.Other",
            ],
        ),
        ({"SphericalProfile": "test", "Other": "toast"}, ["SphericalProfile", "Other"]),
        (
            {"mock_real.SphericalProfile": "test", "mock_real.Other": "toast"},
            ["mock_real.SphericalProfile", "mock_real.Other"],
        ),
        (
            {"mock_real": {"SphericalProfile": "test", "Other": "toast"}},
            ["mock_real", "mock_real.SphericalProfile", "mock_real.Other"],
        ),
    ],
)
def test_paths(config_dict, paths):
    config = aconf.JSONPriorConfig(config_dict)
    assert config.paths == paths


@pytest.mark.parametrize(
    "config_dict",
    [
        {
            "test_autoconf.mock_real.SphericalProfile": "test",
            "test_autoconf.mock_real.Other": "toast",
        },
        {"test_autoconf.mock_real": {"SphericalProfile": "test", "Other": "toast"}},
        {"test_autoconf": {"mock_real": {"SphericalProfile": "test", "Other": "toast"}}},
        {"test_autoconf": {"mock_real.SphericalProfile": "test", "mock_real.Other": "toast"}},
        {"SphericalProfile": "test", "Other": "toast"},
        {"mock_real": {"SphericalProfile": "test", "Other": "toast"}},
    ],
)
def test_config_for_path(geometry_profile_path, config_dict):
    config = aconf.JSONPriorConfig(config_dict)
    assert config(geometry_profile_path) == "test"
    assert config(["test_autoconf", "mock_real", "Other"]) == "toast"


def test_path_double():
    config = aconf.JSONPriorConfig({"mock_real": {"SphericalProfile": "test"}})
    assert config(["something", "mock_real", "mock_real", "SphericalProfile"]) == "test"
