from . import exc
from .tools.decorators import cached_property
from .tools.decorators import xp_cast
from .tools.decorators import xp_add
from .tools.decorators import xp_set
from .conf import Config
from .conf import instance
from .json_prior.config import default_prior
from .json_prior.config import make_config_for_class
from .json_prior.config import path_for_class
from .json_prior.config import JSONPriorConfig

__version__ = "2025.5.10.1"