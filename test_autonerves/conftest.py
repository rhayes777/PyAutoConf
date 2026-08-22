import pathlib

import pytest

from autonerves import conf


@pytest.fixture(scope="session", name="files_directory")
def make_files_directory():
    return pathlib.Path(__file__).parent / "files"


@pytest.fixture(scope="session", name="session_config")
def make_session_config(files_directory):
    return conf.Config(
        files_directory / "config",
        files_directory / "default",
    )


@pytest.fixture(name="config")
def make_config(files_directory):
    return conf.Config(
        files_directory / "config",
        files_directory / "default",
    )


@pytest.fixture(autouse=True)
def _regime_independent_test_output(monkeypatch):
    """
    Clear ``PYAUTO_SMALL_DATASETS`` for every test unless the test sets it.

    Since PyAutoNerves#153 every FITS the stack writes carries a ``SMALLDAT``
    card whose value tracks this env var at write time. Several tests write into
    **tracked** fixture paths (14 of them across PyAutoArray and this repo --
    a pre-existing pattern), so without this the bytes those tests produce
    depend on the ambient environment: run the suite in a shell exporting
    ``PYAUTO_SMALL_DATASETS=1`` -- which ``should_simulate``'s own docstring calls
    the default for most harness runs -- and the suite passes but leaves the
    working tree dirty.

    Pinning it here restores the property the stamp took away, that test output
    is a function of the test and not of the shell, and does so in one place
    rather than by rewriting every fixture-writing test. Tests that need a
    regime set it with ``monkeypatch.setenv`` in their body, which runs after
    this fixture and wins.
    """
    monkeypatch.delenv("PYAUTO_SMALL_DATASETS", raising=False)
