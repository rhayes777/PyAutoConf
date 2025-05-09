from codecs import open
from os.path import abspath, dirname, join
import os

from setuptools import setup

version = os.environ.get("VERSION", "1.0.dev1")

this_dir = abspath(dirname(__file__))

with open(join(this_dir, "requirements.txt")) as f:
    requirements = f.read().split("\n")

setup(
    version=version,
    install_requires=requirements,
)