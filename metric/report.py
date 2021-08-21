from metric import INPUT
from metric.scenario import Scenario


def main():
    scenario = Scenario.from_path(INPUT)

    print(f"\nBASELINE : {scenario.baseline_units:.2f} units")
    print(scenario.baseline_info)

    print(f"\nRETAINED : {scenario.retained_units:.2f} units")
    print(scenario.retained_info)

    print(f"\nENHANCED : {scenario.enhancement_units:.2f} units")
    print(scenario.enhancement_info)

    print(f"\nCREATED : {scenario.creation_units:.2f} units")
    print(scenario.creation_info)

    print("\nTRANSITIONS")
    print(scenario.transitions_info)

    print("\nSUMMARY")
    print(scenario.summary_info)


if __name__ == "__main__":
    main()
