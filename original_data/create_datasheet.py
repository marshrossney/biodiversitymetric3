import pandas as pd

database = pd.DataFrame([])

for f in (
    "distinctiveness.tsv",
    "difficulty.tsv",
    "temporal-creation.tsv",
    "temporal-enhancement.tsv",
):
    df = pd.read_csv(f, sep="\t", index_col=0)

    assert len(df) == 128  # number of habitats

    database = pd.concat((database, df), axis=1)


assert len(df) == 128

database.reset_index(inplace=True)

#tmp = database["Habitat Description"].str.split("-", n=1, expand=True)
#database["Habitat Description"] = tmp[1].str.strip()  # strip leading whitespace

print(database.head())

