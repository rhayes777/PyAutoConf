import pathlib

import pytest

from autoconf import conf


@pytest.fixture(
    name="files_directory"
)
def make_files_directory():
    return pathlib.Path(
        __file__
    ).parent / "files"


@pytest.fixture(
    name="config"
)
def make_config(files_directory):
    return conf.Config(
        files_directory / "config",
        files_directory / "default",
    )
