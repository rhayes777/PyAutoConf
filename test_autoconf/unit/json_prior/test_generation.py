import os

import pytest

import autoconf as aconf


class MyClass:
    def __init__(self, one, two):
        self.one = one
        self.two = two


@pytest.fixture(name="my_class_config")
def make_my_class_config():
    return {"one": aconf.default_prior, "two": aconf.default_prior}


def test_make_config(my_class_config):
    path, value = aconf.make_config_for_class(MyClass)
    assert path == ["json_prior", "test_generation", "MyClass"]
    assert value == my_class_config


@pytest.fixture(name="filename")
def make_filename():
    filename = "priors"
    os.makedirs(filename, exist_ok=True)
    return filename


@pytest.fixture(name="config")
def make_config(filename):
    return aconf.JSONPriorConfig(
        config_dict={
            "test_autoconf.json_prior.test_generation.ClassOne": {"attribute": {}},
            "different_project.json_prior.test_generation.ClassTwo": {"attribute": {}},
            "test_autoconf.json_prior.different_module.ClassThree": {"attribute": {}},
        },
        directory=filename,
    )


@pytest.fixture(name="result", autouse=True)
def make_result(config):
    return config.for_class_and_suffix_path(MyClass, ["one"])


def test_generate(result):
    assert result == aconf.default_prior


def test_rearrange(config, my_class_config):
    assert config.obj == {
        'different_project': {'json_prior.test_generation.ClassTwo.attribute': {}},
        'json_prior': {
            'test_generation.MyClass': {
                'one': {
                    'gaussian_limits': {
                        'lower': 0.0,
                        'upper': 1.0
                    },
                    'lower_limit': 0.0,
                    'type': 'Uniform',
                    'upper_limit': 1.0,
                    'width_modifier': {
                        'type': 'Absolute',
                        'value': 0.2
                    }
                },
                'two': {
                    'gaussian_limits': {
                        'lower': 0.0,
                        'upper': 1.0
                    },
                    'lower_limit': 0.0,
                    'type': 'Uniform',
                    'upper_limit': 1.0,
                    'width_modifier': {
                        'type': 'Absolute',
                        'value': 0.2
                    }
                }
            }
        },
        'test_autoconf': {
            'json_prior': {
                'different_module': {'ClassThree.attribute': {}},
                'test_generation': {'ClassOne.attribute': {}}
            }
        }
    }
