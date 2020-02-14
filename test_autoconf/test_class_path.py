import autoconf as ac
from test_autoconf.mock import GeometryProfile


def test_path_for_class():
    assert ac.path_for_class(
        GeometryProfile
    ) == "test_autoconf.mock.GeometryProfile"


def test_config_for_path():
    assert ac.JSONPriorConfig(
        {
            "test_autoconf.mock.GeometryProfile": "test"
        }
    )(
        "test_autoconf.mock.GeometryProfile"
    ) == "test"
