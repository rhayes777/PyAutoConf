import pathlib

import pytest

from autoconf import conf


@pytest.fixture(
    name="config"
)
def make_config():
    files_directory = pathlib.Path(
        __file__
    ).parent / "files"
    return conf.Config(
        files_directory / "config",
        default_config_paths=(
            files_directory / "default",
        )
    )


def test_override_file(config):
    hpc = config["general"]["hpc"]

    assert hpc["hpc_mode"] is False
    assert hpc["default_field"] == "hello"


def test_override_in_directory(config):
    subscript = config["text"]["label"]["subscript"]

    assert subscript["Galaxy"] == "g"
    assert subscript["default_field"] == "label default"


def test_novel_directory(config):
    assert config["default"]["other"]["section"]["key"] == "value"


def test_novel_file(config):
    assert config["default_file"]["section"]["key"] == "file value"
