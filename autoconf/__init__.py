import sys

if sys.version_info < (3, 12):
    raise RuntimeError(
        f"PyAutoConf requires Python 3.12 or later. "
        f"You are running Python {sys.version_info.major}.{sys.version_info.minor}."
    )

from . import jax_wrapper
from . import exc
from .tools.decorators import cached_property
from .conf import Config
from .conf import instance
from .json_prior.config import default_prior
from .json_prior.config import make_config_for_class
from .json_prior.config import path_for_class
from .json_prior.config import JSONPriorConfig

from .setup_colab import for_autolens
from .setup_notebook import setup_notebook
from .test_mode import test_mode_level, is_test_mode, skip_fit_output, skip_visualization, skip_checks


__version__ = "2026.4.13.3"
