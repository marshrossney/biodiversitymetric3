"""Python implementation of DEFRA & Natural England's Biodiversity Metric 3.0."""
__version__ = "0.1"

import argparse
import json
import pathlib
from types import SimpleNamespace

# Set default configuration file to the one in this directory
_default_config = str(pathlib.Path(__file__).with_name("config.json").resolve())

# NOTE: to be really good boy I should parse individual entries in config.
# However, using jsonargparse to parse as a config file is VERY slowm probably
# because 'habitats' introduces too many levels of nesting
_parser = argparse.ArgumentParser()
_parser.add_argument(
    "-c",
    "--config",
    type=str,
    default=_default_config,
    help="path to JSON configuration file specifying the Metric parameters",
)

# path to input file (entries are later parsed individually)
_parser.add_argument(
    "--input",
    type=str,
    required=False,
    help="path to JSON or YAML configuration file specifying the habitat parcels",
)

_args = _parser.parse_args()

with open(_args.config, "r") as fp:
    CONFIG = SimpleNamespace(**json.load(fp))

INPUT = _args.input
