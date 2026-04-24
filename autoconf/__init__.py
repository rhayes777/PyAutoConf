"""
autoconf — configuration, serialization, and I/O helpers for the PyAuto ecosystem.

Text-format I/O surfaces:

- :mod:`autoconf.dictable`  — JSON (``output_to_json`` / ``from_json``)
- :mod:`autoconf.fitsable`  — FITS (``output_to_fits`` / ``ndarray_via_fits_from``)
- :mod:`autoconf.csvable`   — CSV  (``output_to_csv`` / ``list_from_csv``)
"""
import sys
from pathlib import Path


def _python_version_check_bypassed():
    """
    Return True iff the user's workspace config disables the Python version check.

    Reads ``<cwd>/config/general.yaml`` and looks for ``version.python_version_check``.
    Any failure (missing file, unreadable YAML, missing key, missing yaml module) is
    treated as "not bypassed" so the default check still fires.
    """
    try:
        import yaml

        config_path = Path.cwd() / "config" / "general.yaml"
        with config_path.open("r") as f:
            data = yaml.safe_load(f) or {}
        return data.get("version", {}).get("python_version_check") is False
    except Exception:
        return False


if sys.version_info < (3, 12) and not _python_version_check_bypassed():
    raise RuntimeError(
        f"Python {sys.version_info.major}.{sys.version_info.minor} detected. "
        f"PyAutoConf is officially supported on Python 3.12+.\n"
        f"Python 3.9, 3.10, and 3.11 will technically work but are not tested against.\n"
        f"\n"
        f"To bypass this check, add the following to your config/general.yaml:\n"
        f"\n"
        f"  version:\n"
        f"    python_version_check: False\n"
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
from .workspace import check_version, WorkspaceVersionMismatchError


__version__ = "2026.4.13.6"
