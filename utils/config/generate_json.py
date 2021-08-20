"""Script for building JSON config file using tabulated values taken from the Excel tool.

See http://publications.naturalengland.org.uk/publication/6049804846366720
"""
import json
from pathlib import Path
from pprint import pprint

import pandas as pd

data_dir = Path("exported_data")

def load(path_to_file: Path):
    df = pd.read_csv(path_to_file.resolve(), sep="\t")

    # Get rid of the broad habitat class (Woodland, Grassland etc)
    tmp = df["Habitat Description"].str.split("-", n=1, expand=True)
    df["Habitat Description"] = tmp[1].str.strip()
    df.set_index("Habitat Description", inplace=True)

    assert len(df) == 128  # expected number of habitats

    return df


single_attributes = [
    load(data_dir / f"{f}.tsv")
    for f in (
        "groups",
        "distinctiveness",
        "creation_difficulty",
        "enhancement_difficulty",
    )
]
habitats = pd.concat(single_attributes, axis=1).to_dict(orient="index")

creation_time = load(data_dir / "creation_time.tsv").to_dict(orient="index")
enhancement_time = load(data_dir / "enhancement_time.tsv").to_dict(orient="index")

for h in habitats.keys():
    habitats[h].update(
        creation_time=creation_time[h], enhancement_time=enhancement_time[h]
    )

pprint(habitats["Artificial littoral mud"])  # sanity check

habitats = dict(habitats=habitats)  # single-item dict with 'habitats' as the key

with open(data_dir / "globals.json", "r") as fp:
    globals_ = json.load(fp)

with open("config.json", "w") as fp:
    json.dump(globals_ | habitats, fp, indent=6)
