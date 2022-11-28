class JSONClass:
    def __init__(self, variable: float):
        self.variable = variable


class YAMLClass:
    def __init__(self, variable: float):
        self.variable = variable


def test_load_json_config(config):
    assert config.prior_config.for_class_and_suffix_path(JSONClass, ["variable"]) == {
        "lower_limit": 0.0,
        "type": "Uniform",
        "upper_limit": 3.0,
    }


def test_load_yaml_config(config):
    assert config.prior_config.for_class_and_suffix_path(YAMLClass, ["variable"]) == {
        "lower_limit": 0.0,
        "type": "Uniform",
        "upper_limit": 3.0,
    }
