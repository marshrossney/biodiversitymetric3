"""Script to convert tab-separated data (as exported from Excel) to JSON input file."""
import argparse
import json
import pathlib
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "input",
    type=str,
    help="path to table of habitat parcels",
)
parser.add_argument(
    "-t",
    "--type",
    type=str,
    required=False,
    choices=["baseline", "created", "enhanced"],
    default="baseline",
    help="type of scenario, options: 'baseline', 'created', 'enhanced', default: 'baseline'",
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    required=False,
    default=None,
    help="optional name for output JSON file, default: <input>.json",
)

args = parser.parse_args()

if args.output is not None:
    outfile = args.output
else:
    outfile = pathlib.Path(args.input).stem + ".json"

df = pd.read_csv(args.input, sep="\t")

letter = args.type[0]  # b, e or c
df["pid"] = [f"{letter}{i+1}" for i in df.index]

# Output {'baseline' : [{b1}, {b2} ...]}
dict_out = {args.type: df.to_dict(orient="records")}

with open(outfile, "w") as fp:
    json.dump(dict_out, fp, indent=6)
