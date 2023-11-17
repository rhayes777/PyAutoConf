import pytest

from autoconf import instance
from autoconf.output import conditional_output


class OutputClass:
    def __init__(self):
        self.output_names = []

    @conditional_output
    def output_function(self, name):
        self.output_names.append(name)


@pytest.fixture(name="output_class")
def make_output_class():
    return OutputClass()


@pytest.fixture(autouse=True)
def add_config(files_directory):
    instance.push(files_directory / "config")


def test_output(output_class):
    output_class.output_function("should_output")
    assert output_class.output_names == ["should_output"]


def test_no_output(output_class):
    output_class.output_function("should_not_output")
    assert output_class.output_names == []
