import os
from pathlib import Path

from autoconf.json_prior.config import JSONPriorConfig
from autoconf.json_prior.converter import convert
from autoconf.named import NamedConfig, AbstractConfig


def get_matplotlib_backend():
    try:
        return instance["visualize_general"]["general"]["backend"]
    except KeyError:
        return "default"


class RecursiveConfig(AbstractConfig):
    def __init__(self, path, default_configs=tuple()):
        super().__init__(default_configs)
        self.path = Path(path)

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.path}>"

    def __getitem__(self, item):
        item_path = self.path / f"{item}"
        file_path = f"{item_path}.ini"
        default_configs = self._default_configs_for_item(
            item
        )
        if os.path.isfile(file_path):
            return NamedConfig(
                file_path,
                default_configs=default_configs
            )
        if os.path.isdir(item_path):
            return RecursiveConfig(
                item_path,
                default_configs=default_configs
            )
        raise KeyError(
            f"No configuration found for {item} at path {self.path}"
        )


class Config(RecursiveConfig):
    def __init__(self, config_path, output_path="output", default_config_paths=tuple()):
        super().__init__(config_path)
        json_config_path = f"{config_path}/json_priors"
        if not os.path.exists(json_config_path):
            convert(f"{config_path}/priors", json_config_path)
        self.prior_config = JSONPriorConfig.from_directory(json_config_path)

        self._default_configs = list(map(
            RecursiveConfig,
            default_config_paths
        ))

        # self.non_linear = NamedConfig(f"{config_path}/non_linear")
        # self.optimize = NamedConfig(f"{config_path}/non_linear/optimize")
        # self.mcmc = NamedConfig(f"{config_path}/non_linear/mcmc")
        # self.nest = NamedConfig(f"{config_path}/non_linear/nest")
        # self.mock = NamedConfig(f"{config_path}/non_linear/mock")
        #
        # self.label = NamedConfig("{}/notation/label.ini".format(config_path))
        # self.label_format = NamedConfig("{}/notation/label_format.ini".format(config_path))
        # self.settings_tag = NamedConfig("{}/notation/settings_tags.ini".format(config_path))
        # self.setup_tag = NamedConfig("{}/notation/setup_tags.ini".format(config_path))
        # self.general = NamedConfig("{}/general.ini".format(config_path))
        # self.visualize_general = NamedConfig("{}/visualize/general.ini".format(config_path))
        # self.visualize_plots = NamedConfig("{}/visualize/plots.ini".format(config_path))
        # self.visualize_figures = NamedConfig("{}/visualize/figures.ini".format(config_path))
        # self.visualize_subplots = NamedConfig("{}/visualize/subplots.ini".format(config_path))
        # self.interpolate = NamedConfig("{}/grids/interpolate.ini".format(config_path))
        # self.radial_min = NamedConfig("{}/grids/radial_minimum.ini".format(config_path))
        self.output_path = output_path

    def add_default(self, config_path):
        self._default_configs.append(
            RecursiveConfig(config_path)
        )

    @classmethod
    def for_directory(cls, directory):
        directory_path = Path(directory)
        return Config(
            directory_path / "config",
            directory_path / "output"
        )


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
