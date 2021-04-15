import pytest

import autoconf as aconf
from autoconf.mock.mock_real import SphProfile


@pytest.fixture(name="geometry_profile_path")
def make_geometry_profile_path():
    return ["autoconf", "mock", "mock_real", "SphProfile"]


def test_path_for_class(geometry_profile_path):
    assert aconf.path_for_class(SphProfile) == geometry_profile_path


@pytest.mark.parametrize(
    "config_dict, paths",
    [
        (
            {
                "autoconf.mock.mock_real.SphProfile": "test",
                "autoconf.mock.mock_real.Other": "toast",
            },
            ["autoconf.mock.mock_real.SphProfile", "autoconf.mock.mock_real.Other"],
        ),
        (
            {"autoconf.mock.mock_real": {"SphProfile": "test", "Other": "toast"}},
            [
                "autoconf.mock.mock_real",
                "autoconf.mock.mock_real.SphProfile",
                "autoconf.mock.mock_real.Other",
            ],
        ),
        (
            {"autoconf": {"mock": {"mock_real": {"SphProfile": "test", "Other": "toast"}}}},
            [
                "autoconf",
                "autoconf.mock",
                "autoconf.mock.mock_real",
                "autoconf.mock.mock_real.SphProfile",
                "autoconf.mock.mock_real.Other",
            ],
        ),
        (
            {"autoconf": {"mock": {"mock_real.SphProfile": "test", "mock_real.Other": "toast"}}},
            [
                "autoconf",
                "autoconf.mock",
                "autoconf.mock.mock_real.SphProfile",
                "autoconf.mock.mock_real.Other",
            ],
        ),
        ({"SphProfile": "test", "Other": "toast"}, ["SphProfile", "Other"]),
        (
            {"mock_real.SphProfile": "test", "mock_real.Other": "toast"},
            ["mock_real.SphProfile", "mock_real.Other"],
        ),
        (
            {"mock_real": {"SphProfile": "test", "Other": "toast"}},
            ["mock_real", "mock_real.SphProfile", "mock_real.Other"],
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
            "autoconf.mock.mock_real.SphProfile": "test",
            "autoconf.mock.mock_real.Other": "toast",
        },
        {"autoconf.mock.mock_real": {"SphProfile": "test", "Other": "toast"}},
        {"autoconf":{"mock": {"mock_real": {"SphProfile": "test", "Other": "toast"}}}},
        {"autoconf":{"mock": {"mock_real.SphProfile": "test", "mock_real.Other": "toast"}}},
        {"SphProfile": "test", "Other": "toast"},
        {"mock_real": {"SphProfile": "test", "Other": "toast"}},
    ],
)
def test_config_for_path(geometry_profile_path, config_dict):
    config = aconf.JSONPriorConfig(config_dict)
    assert config(geometry_profile_path) == "test"
    assert config(["autoconf", "mock", "mock_real", "Other"]) == "toast"


def test_path_double():
    config = aconf.JSONPriorConfig({"mock_real": {"SphProfile": "test"}})
    assert config(["something", "mock_real", "mock_real", "SphProfile"]) == "test"
