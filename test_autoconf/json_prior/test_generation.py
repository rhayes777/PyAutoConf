import autoconf as ac


class MyClass:
    def __init__(self, one, two):
        self.one = one
        self.two = two


def test_make_config():
    path, value = ac.make_config_for_class(
        MyClass
    )
    assert path == "test_autoconf.json_prior.test_generation.MyClass"
    assert value == {
        "one": ac.default_prior,
        "two": ac.default_prior
    }


def test_generate():
    config = ac.JSONPriorConfig(
        {},
        directory="priors.json"
    )

    result = config.for_class_and_suffix_path(
        MyClass,
        ["one"]
    )

    assert result == ac.default_prior
