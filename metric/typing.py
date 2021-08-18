from collections import namedtuple
from enum import Enum
import json
from types import SimpleNamespace

from fuzzywuzzy import process

with open("config.json", "r") as fp:
    config = SimpleNamespace(**json.load(fp))

# Categories that have been assigned numerical values...
Distinctiveness = Enum("Distinctiveness", config.distinctiveness)
Condition = Enum("Condition", config.condition)
StrategicSignificance = Enum("StrategicSignificance", config.strategic_significance)
Difficulty = Enum("Difficulty", config.difficulty)
SpatialRisk = Enum("SpatialRisk", config.spatial_risk)

# How to do habitat class
