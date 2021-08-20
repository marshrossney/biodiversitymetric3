from metric import INPUT
from metric.scenario import Scenario



def main():
    scenario = Scenario.from_path(INPUT)

    print(scenario.metric_score)


if __name__ == "__main__":
    main()
