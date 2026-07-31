"""
autonerves — configuration, serialization, and I/O helpers for the PyAuto ecosystem.

Text-format I/O surfaces:

- :mod:`autonerves.dictable`  — JSON (``output_to_json`` / ``from_json``)
- :mod:`autonerves.fitsable`  — FITS (``output_to_fits`` / ``ndarray_via_fits_from``)
- :mod:`autonerves.csvable`   — CSV  (``output_to_csv`` / ``list_from_csv``)
"""
import sys
import warnings
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


_RECOMMENDED_PYTHON_VERSIONS = {(3, 12), (3, 13), (3, 14)}


def _emit_python_version_warning():
    current = sys.version_info[:2]
    if current in _RECOMMENDED_PYTHON_VERSIONS:
        return
    if _python_version_check_bypassed():
        return

    py = f"{current[0]}.{current[1]}"
    supported = [
        f"{major}.{minor}" for major, minor in sorted(_RECOMMENDED_PYTHON_VERSIONS)
    ]
    prose = ", ".join(supported[:-1]) + " and " + supported[-1]
    choice = ", ".join(supported[:-1]) + " or " + supported[-1]
    slash = "/".join(supported)
    if current < (3, 12):
        lines = [
            f"PyAuto: Python {py} detected -- Python 3.12 or newer is required.",
            "",
            "This Python version is unsupported by current PyAuto releases.",
            f"Install Python {choice}, or pin a pre-migration PyAuto release.",
        ]
        warning = (
            f"PyAuto: running on unsupported Python {py}; current releases "
            "require Python >=3.12."
        )
    else:
        lines = [
            f"PyAuto: Python {py} detected -- this Python version is experimental.",
            "",
            f"PyAuto currently tests and supports Python {prose}.",
            f"Python {py} may encounter known compatibility issues.",
            f"Use Python {choice} for production work.",
        ]
        warning = (
            f"PyAuto: running on experimental Python {py}; supported versions "
            f"are {slash}."
        )
    lines.extend(
        [
            "",
            "To silence this warning, add to <cwd>/config/general.yaml:",
            "",
            "    version:",
            "      python_version_check: False",
        ]
    )

    inner_width = max(len(line) for line in lines)
    border = "+" + "-" * (inner_width + 4) + "+"
    framed = [border]
    for line in lines:
        framed.append("|  " + line.ljust(inner_width) + "  |")
    framed.append(border)

    print("\n".join(framed), file=sys.stderr)
    warnings.warn(
        warning
        + " Suppress this warning via 'version.python_version_check: False' "
        "in config/general.yaml.",
        UserWarning,
        stacklevel=2,
    )


_emit_python_version_warning()

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


__version__ = "2026.7.23.1"
