import inspect
import json
import logging
import os
from os import path
from importlib import util
from pathlib import Path

from .config import make_config_for_class

logger = logging.getLogger(__name__)


def for_file(module_path: str) -> dict:
    """
    Generate JSON priors for all classes in a file, using default
    prior configuration for each constructor argument.

    Parameters
    ----------
    module_path
        The path to the file.

    Returns
    -------
    JSON configuration, where class names are mapped to their prior configs.
    """
    spec = util.spec_from_file_location("module.name", module_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    classes = inspect.getmembers(module)

    return {
        name: make_config_for_class(obj)[1]
        for name, obj in classes
        if inspect.isclass(obj)
    }


def generate(directory: str, output_directory=Path(os.getcwd()) / "priors"):
    """
    Generate prior configuration for a given directory, recursively.

    A directory "priors" is created if it does not exists. A new JSON file is created
    in priors for each python module found that contains at least one class.

    If an output file already exists then prior generation is skipped.

    Parameters
    ----------
    output_directory
        Where to output the prior configuration files
    directory
        The directory for which prior are generated
    """
    os.makedirs(output_directory, exist_ok=True)

    for directory, _, files in os.walk(directory):
        directory = Path(directory)
        for file in files:
            if file.endswith(".py"):
                full_path = directory / file
                spec = for_file(full_path)
                config_path = output_directory / file.replace(".py", ".json")
                if len(spec) > 0:
                    if os.path.exists(config_path):
                        logger.info(f"{config_path} already exists")
                        continue
                    with open(config_path, "w+") as f:
                        json.dump(spec, f)
