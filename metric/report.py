from metric.core import load_scenario

scenario = load_scenario()

def main():

    print("Baseline")
    print("-------------")
    for pid, parcel in scenario.baseline.items():
        print(pid, " : ", parcel.biodiversity_units)

    sum_ = sum([parcel.biodiversity_units for parcel in scenario.baseline.values()])
    print(f"Sum = {sum_}")

    print("")

    print("Creation")
    print("-------------")
    for pid, parcel in scenario.creation.items():
        print(pid, " : ", parcel.creation_units)
    sum_ = sum([parcel.creation_units for parcel in scenario.creation.values()])
    print(f"Sum = {sum_}")

    print("")
    print("Enhancement")
    print("-------------")
    for pid, parcel in scenario.enhancement.items():
        print(pid, " : ", parcel.enhancement_units(scenario.baseline[parcel.baseline_pid]))
    sum_ = sum([parcel.enhancement_units(scenario.baseline[parcel.baseline_pid]) for parcel in scenario.enhancement.values()])
    print(f"Sum = {sum_}")

if __name__ == "__main__":
    main()
