import inspect
import json
import logging
import os
from importlib import util

from .config import make_config_for_class

logger = logging.getLogger(__name__)


def for_file(module_path):
    spec = util.spec_from_file_location(
        "module.name",
        module_path
    )
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    classes = inspect.getmembers(module)

    return {
        name: make_config_for_class(obj)[1]
        for name, obj in classes
        if inspect.isclass(obj)
    }


def generate(directory):
    try:
        os.mkdir(f"{directory}/priors")
    except FileExistsError:
        pass
    for directory, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = f"{directory}/{file}"
                spec = for_file(full_path)
                config_path = f"priors/{file.replace('.py', '.json')}"
                if len(spec) > 0:
                    if os.path.exists(config_path):
                        logger.info(f"{config_path} already exists")
                        continue
                    with open(config_path, "w+") as f:
                        json.dump(spec, f)
