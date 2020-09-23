import os

from autoconf.json_prior.config import JSONPriorConfig
from autoconf.json_prior.converter import convert
from autoconf.named import NamedConfig


def get_matplotlib_backend():
    return instance.visualize_general.get("general", "backend", str)


class Config:
    def __init__(self, config_path, output_path="output"):
        self.config_path = config_path
        json_config_path = f"{config_path}/json_priors"
        if not os.path.exists(json_config_path):
            convert(f"{config_path}/priors", json_config_path)
        self.prior_config = JSONPriorConfig.from_directory(json_config_path)

        self.non_linear = NamedConfig(
            f"{config_path}/non_linear"
        )
        self.optimize = NamedConfig(
            f"{config_path}/non_linear/optimize"
        )
        self.mcmc = NamedConfig(
            f"{config_path}/non_linear/mcmc"
        )
        self.nest = NamedConfig(
            f"{config_path}/non_linear/nest"
        )
        self.mock = NamedConfig(
            f"{config_path}/non_linear/mock"
        )

        self.label = NamedConfig("{}/notation/label.ini".format(config_path))
        self.label_format = NamedConfig("{}/notation/label_format.ini".format(config_path))
        self.settings_tag = NamedConfig("{}/notation/settings_tags.ini".format(config_path))
        self.setup_tag = NamedConfig("{}/notation/setup_tags.ini".format(config_path))
        self.general = NamedConfig("{}/general.ini".format(config_path))
        self.visualize_general = NamedConfig(
            "{}/visualize/general.ini".format(config_path)
        )
        self.visualize_plots = NamedConfig("{}/visualize/plots.ini".format(config_path))
        self.visualize_figures = NamedConfig(
            "{}/visualize/figures.ini".format(config_path)
        )
        self.visualize_subplots = NamedConfig(
            "{}/visualize/subplots.ini".format(config_path)
        )
        self.interpolate = NamedConfig(
            "{}/grids/interpolate.ini".format(config_path)
        )
        self.radial_min = NamedConfig(
            "{}/grids/radial_minimum.ini".format(config_path)
        )
        self.output_path = output_path


def is_config_in(folder):
    return os.path.isdir("{}/config".format(folder))


current_directory = os.getcwd()

workspace_path = os.environ.get(
    "WORKSPACE",
    current_directory
)
default = Config(
    f"{workspace_path}/config",
    f"{workspace_path}/output/"
)

instance = default
