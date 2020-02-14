import pytest

import autoconf as ac
from test_autoconf.mock import GeometryProfile


@pytest.fixture(
    name="geometry_profile_path"
)
def make_geometry_profile_path():
    return ["test_autoconf", "mock", "GeometryProfile"]


def test_path_for_class(geometry_profile_path):
    assert ac.path_for_class(
        GeometryProfile
    ) == geometry_profile_path


@pytest.mark.parametrize(
    "config_dict",
    [
        {
            "test_autoconf.mock.GeometryProfile": "test"
        },
        {
            "test_autoconf.mock": {"GeometryProfile": "test"}
        },
        {
            "test_autoconf": {"mock": {"GeometryProfile": "test"}}
        },
        {
            "test_autoconf": {"mock.GeometryProfile": "test"}
        },
        {
            "*.GeometryProfile": "test"
        },
        {
            "*.mock.GeometryProfile": "test"
        },
        {
            "*.mock": {"GeometryProfile": "test"}
        },
        {
            "test_autoconf": {"*.GeometryProfile": "test"}
        }
    ]
)
def test_config_for_path(
        geometry_profile_path,
        config_dict
):
    assert ac.JSONPriorConfig(
        config_dict
    )(
        geometry_profile_path
    ) == "test"
