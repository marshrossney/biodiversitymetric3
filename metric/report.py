from jsonargparse import ArgumentParser, namespace_to_dict

from metric import INPUT
from metric.core import HabitatParcel

parser = ArgumentParser()
parser.add_argument("--baseline", type=HabitatParcel, nargs="+")

scenario = parser.parse_path(INPUT)


def main():

    for parcel in scenario.baseline:
        p = HabitatParcel(**namespace_to_dict(parcel))
        print(p.biodiversity_units)


if __name__ == "__main__":
    main()
