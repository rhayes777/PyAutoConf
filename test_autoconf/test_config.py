from os import path

import pytest

import autoconf as ac

directory = path.dirname(path.realpath(__file__))

from test_autoconf.mock import EllipticalLP, EllipticalGaussian


class MockClass(object):
    pass


@pytest.fixture(name="label_config")
def make_label_config():
    return ac.conf.LabelConfig("{}/test_files/config/label.ini".format(directory))


class TestLabel:
    def test_basic(self, label_config):
        assert label_config.label("centre_0") == "x"
        assert label_config.label("redshift") == "z"

    def test_escaped(self, label_config):
        assert label_config.label("gamma") == r"\gamma"
        assert label_config.label("contribution_factor") == r"\omega0"

    def test_subscript(self, label_config):
        assert label_config.subscript(EllipticalLP) == "l"

    def test_inheritance(self, label_config):
        assert label_config.subscript(EllipticalGaussian) == "l"

    def test_exception(self, label_config):
        with pytest.raises(ac.exc.PriorException):
            label_config.subscript(MockClass)
