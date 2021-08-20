import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", type=str, required=True, help="name for output JSON file")
parser.add_argument("inputs", type=str, nargs="+", help="input JSON files")

args = parser.parse_args()

out = {}
for infile in args.inputs:
    with open(infile, "r") as fp:
        out.update(**json.load(fp))

with open(args.output, "w") as fp:
    json.dump(out, fp, indent=6)
