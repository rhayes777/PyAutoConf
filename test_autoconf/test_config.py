import os
import shutil
from os import path

import pytest

from autoconf import conf
from autoconf.directory_config import NamedConfig
from autoconf.exc import ConfigException
from autoconf.mock.mock_real import EllProfile, EllGaussian

directory = path.dirname(path.realpath(__file__))


class MockClass:
    pass


@pytest.fixture(name="label_config")
def make_label_config():
    return NamedConfig(
        "{}/files/config/label.ini".format(directory)
    )


class TestLabel:
    def test_basic(self, label_config):
        assert label_config["label"]["centre_0"] == "x"
        assert label_config["label"]["redshift"] == "z"

    def test_escaped(self, label_config):
        assert label_config["label"]["gamma"] == r"\gamma"
        assert label_config["label"]["contribution_factor"] == r"\omega0"

    def test_superscript(self, label_config):
        assert label_config["superscript"].family(EllProfile) == "l"

    def test_inheritance(self, label_config):
        assert label_config["superscript"].family(EllGaussian) == "l"

    def test_exception(self, label_config):
        with pytest.raises(KeyError):
            label_config["superscript"].family(MockClass)


BAD_PATH = "bad/path"


def remove_path():
    shutil.rmtree(
        BAD_PATH,
        ignore_errors=True,
    )


@pytest.fixture(
    name="config"
)
def make_config():
    return conf.Config()


def test_path_does_not_exist(config):
    remove_path()
    with pytest.raises(ConfigException):
        config.push(BAD_PATH)


def test_path_empty(config):
    os.makedirs(BAD_PATH, exist_ok=True)
    with pytest.raises(ConfigException):
        config.push(BAD_PATH)
