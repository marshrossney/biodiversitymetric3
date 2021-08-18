import json
from types import SimpleNamespace

from jsonargparse import ArgumentParser, ActionConfigFile, namespace_to_dict
from jsonargparse.typing import final, PositiveInt, PositiveFloat

from metric.core import HabitatParcel

with open("config.json", "r") as fp:
    config = SimpleNamespace(**json.load(fp))

parser = ArgumentParser()
# parser.add_argument("-c", "--config", action=ActionConfigFile)
parser.add_argument("--baseline", type=HabitatParcel, nargs="+")

params = parser.parse_path("turnden.yml")


def main():

    for parcel in params.baseline:
        p = HabitatParcel(**namespace_to_dict(parcel))
        print(p.biodiversity_units)


if __name__ == "__main__":
    main()
