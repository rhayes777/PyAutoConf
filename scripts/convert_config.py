#!/usr/bin/env python

import sys

import yaml

from autoconf.directory_config import RecursiveConfig
from autofit.mapper.prior_model.abstract import Path

target_path = Path(sys.argv[0])

config = RecursiveConfig(target_path)

for key in config.keys():
    with open((target_path / key).with_suffix(".yaml"), "w") as f:
        yaml.dump(config[key].dict(), f)
