#!/usr/bin/env python
import os
import shutil
import sys
from pathlib import Path

import yaml

from autoconf.directory_config import RecursiveConfig

target_path = Path(sys.argv[1])

config = RecursiveConfig(str(target_path))

for key in config.keys():
    d = config[key].dict()
    path = target_path / key
    with open(path.with_suffix(".yaml"), "w") as f:
        yaml.dump(d, f)

    try:
        os.remove(path.with_suffix(".ini"))
    except FileNotFoundError:
        pass

    shutil.rmtree(path, ignore_errors=True)
