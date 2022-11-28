#!/usr/bin/env python
"""
Converts JSON prior configs to YAML equivalent.

Usage:
./convert_prior_configs.py /path/to/prior/directory
"""
import json
import os
import sys
from pathlib import Path

import yaml

for path in Path(sys.argv[1]).rglob("*.json"):
    with open(path) as f:
        d = json.load(f)

    with open(path.with_suffix(".yaml"), "w") as f:
        yaml.dump(d, f)

    os.remove(path)
