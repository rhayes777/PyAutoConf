import autoconf as ac
from test_autoconf.mock import GeometryProfile
import pytest


@pytest.fixture(
    name="geometry_profile_path"
)
def make_geometry_profile_path():
    return "test_autoconf.mock.GeometryProfile"


def test_path_for_class(geometry_profile_path):
    assert ac.path_for_class(
        GeometryProfile
    ) == geometry_profile_path


def test_config_for_path(geometry_profile_path):
    assert ac.JSONPriorConfig(
        {
            "test_autoconf.mock.GeometryProfile": "test"
        }
    )(
        geometry_profile_path
    ) == "test"
