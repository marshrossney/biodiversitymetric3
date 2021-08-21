from typing import Optional

import jsonargparse
import tabulate

from metric.habitat import HabitatParcel, HabitatParcelInput

tabulate.PRESERVE_WHITESPACE = True

_parser = jsonargparse.ArgumentParser()
_parser.add_argument("--baseline", type=HabitatParcel, nargs="+")
_parser.add_argument("--retained", type=str, nargs="+")
_parser.add_argument("--created", type=HabitatParcel, nargs="+")
_parser.add_argument("--enhanced", type=HabitatParcel, nargs="+")


class Scenario:
    """Class representing development scenario.

    Args:
        baseline: list[HabitatParcelInput]
        retained: Optional[list[str]]
        created: Optional[list[HabitatParcelInput]]
        enhanced: Optional[list[HabitatParcelInput]]
    """

    tablefmt = "pretty"
    floatfmt = ".2f"  # this appears not to be working

    def __init__(
        self,
        baseline: list[HabitatParcelInput],
        *,
        retained: Optional[list[str]] = [],
        enhanced: Optional[list[HabitatParcelInput]] = [],
        created: Optional[list[HabitatParcelInput]] = [],
    ):
        self._baseline = {p["pid"]: HabitatParcel(**p) for p in baseline}
        # NOTE: empty dicts in case of no input -> evals to BU = 0
        self._retained = retained
        self._created = {p["pid"]: HabitatParcel(**p) for p in created}
        self._enhanced = {p["pid"]: HabitatParcel(**p) for p in enhanced}

    @classmethod
    def from_path(cls, path: str) -> "Scenario":
        """Parses JSON input file and instantiates Scenario object."""
        habitats = jsonargparse.namespace_to_dict(_parser.parse_path(path))
        return cls(
            baseline=habitats["baseline"],
            retained=habitats["retained"],
            enhanced=habitats["enhanced"],
            created=habitats["created"],
        )

    @property
    def baseline(self) -> dict[str, list[HabitatParcel]]:
        """Dict of baseline habitat parcels, indexed by pid."""
        return self._baseline

    @property
    def retained(self) -> list[str]:
        """List of pid's of retained baseline parcels."""
        return self._retained

    @property
    def created(self) -> dict[str, list[HabitatParcel]]:
        """Dict of created habitat parcels, indexed by pid."""
        return self._created

    @property
    def enhanced(self) -> dict[str, list[HabitatParcel]]:
        """Dict of enhanced habitat parcels, indexed by pid."""
        return self._enhanced

    @property
    def baseline_area(self) -> float:
        """Total area of baseline habitat parcels."""
        return sum([parcel.area for parcel in self.baseline.values()])

    @property
    def retained_area(self) -> float:
        """Total area of retained habitat parcels."""
        return sum(
            [
                parcel.area
                for pid, parcel in self.baseline.items()
                if pid in self.retained
            ]
        )

    @property
    def creation_area(self) -> float:
        """Total area of created habitat parcels."""
        return sum([parcel.area for parcel in self.created.values()])

    @property
    def enhancement_area(self) -> float:
        """Total area of enhanced habitat parcels."""
        return sum([parcel.area for parcel in self.enhanced.values()])

    @property
    def post_intervention_area(self) -> float:
        """Total area of retained, created and enhanced parcels."""
        return self.retained_area + self.creation_area + self.enhancement_area

    @property
    def baseline_units(self) -> float:
        """Total Biodiversity Units from the baseline habitat parcels."""
        return sum([parcel.biodiversity_units for parcel in self.baseline.values()])

    @property
    def retained_units(self) -> float:
        """Total Biodiversity Units from the retained habitat parcels."""
        return sum(
            [
                parcel.biodiversity_units
                for pid, parcel in self.baseline.items()
                if pid in self.retained
            ]
        )

    @property
    def creation_units(self) -> float:
        """Total Biodiversity Units from the created habitat parcels."""
        return sum([parcel.creation_units for parcel in self.created.values()])

    @property
    def enhancement_units(self) -> float:
        """Total Biodiversity Units from the enhanced habitat parcels."""
        return sum(
            [
                parcel.enhancement_units(self.baseline[parcel.baseline_pid])
                for parcel in self.enhanced.values()
            ]
        )

    @property
    def post_intervention_units(self) -> float:
        """Total Biodiversity Units from the retained, created and enhanced parcels."""
        return self.retained_units + self.creation_units + self.enhancement_units

    @property
    def metric_score(self) -> float:
        """Percent change in Biodiversity Units, relative to baseline."""
        baseline = self.baseline_units
        return (self.post_intervention_units - baseline) / baseline * 100

    @property
    def baseline_info(self) -> str:
        """Tabulate information on baseline habitat parcels."""
        headers = [
            "ID",
            "Habitat Class",
            "Area",
            "Distinctiveness",
            "Condition",
            "Strategic\nSignificance",
            "Units",
        ]
        data = [
            [
                p.pid,
                p.habitat,
                p.area,
                f"{p.distinctiveness.name} ({p.distinctiveness.value})",
                f"{p.condition.name} ({p.condition.value})",
                f"{p.strategic_significance.name} ({p.strategic_significance.value})",
                f"{p.biodiversity_units:.2f}",
            ]
            for p in self.baseline.values()
        ]
        return tabulate.tabulate(
            data, headers=headers, tablefmt=self.tablefmt, floatfmt=self.floatfmt
        )

    @property
    def retained_info(self) -> str:
        """Tabulate information on retained habitat parcels."""
        headers = [
            "ID",
            "Habitat Class",
            "Area",
            "Distinctiveness",
            "Condition",
            "Strategic\nSignificance",
            "Units",
        ]
        data = [
            [
                p.pid,
                p.habitat,
                p.area,
                f"{p.distinctiveness.name} ({p.distinctiveness.value})",
                f"{p.condition.name} ({p.condition.value})",
                f"{p.strategic_significance.name} ({p.strategic_significance.value})",
                f"{p.biodiversity_units:.2f}",
            ]
            for pid, p in self.baseline.items()
            if pid in self.retained
        ]
        return tabulate.tabulate(
            data, headers=headers, tablefmt=self.tablefmt, floatfmt=self.floatfmt
        )

    @property
    def enhancement_info(self) -> str:
        """Tabulate information on enhanced habitat parcels."""
        headers = [
            "ID",
            "Baseline",
            "Habitat Class",
            "Area",
            "Distinctiveness",
            "Condition",
            "Strategic\nSignificance",
            "Difficulty",
            "Time",
            "Units",
        ]
        data = [
            [
                p.pid,
                p.baseline_pid,
                p.habitat,
                p.area,
                f"{p.distinctiveness.name} ({p.distinctiveness.value})",
                f"{p.condition.name} ({p.condition.value}",
                f"{p.strategic_significance.name} ({p.strategic_significance.value})",
                f"{p.enhancement_difficulty.name} ({p.enhancement_difficulty.value})",
                f"{p.enhancement_time(self.baseline[p.baseline_pid]).time:g}y ({p.enhancement_time(self.baseline[p.baseline_pid]).penalty:.2f})",
                f"{p.enhancement_units(self.baseline[p.baseline_pid]):.2f}",
            ]
            for p in self.enhanced.values()
        ]
        return tabulate.tabulate(
            data, headers=headers, tablefmt=self.tablefmt, floatfmt=self.floatfmt
        )

    @property
    def creation_info(self) -> str:
        """Tabulate information created habitat parcels."""
        headers = [
            "ID",
            "Baseline",
            "Habitat Class",
            "Area",
            "Distinctiveness",
            "Condition",
            "Strategic\nSignificance",
            "Difficulty",
            "Time",
            "Units",
        ]
        data = [
            [
                p.pid,
                p.baseline_pid,
                p.habitat,
                p.area,
                f"{p.distinctiveness.name} ({p.distinctiveness.value})",
                f"{p.condition.name} ({p.condition.value})",
                f"{p.strategic_significance.name} ({p.strategic_significance.value})",
                f"{p.creation_difficulty.name} ({p.creation_difficulty.value})",
                f"{p.creation_time.time:g}y ({p.creation_time.penalty:.2f})",
                f"{p.creation_units:.2f}",
            ]
            for p in self.created.values()
        ]
        return tabulate.tabulate(
            data, headers=headers, tablefmt=self.tablefmt, floatfmt=self.floatfmt
        )

    @property
    def transitions_info(self) -> str:
        """Tabulate summary of transitions."""
        # NOTE: Assumes 1-1 baseline-enhancement or baseline-creation
        headers = [
            "ID",
            "Habitat Class",
            "Distinctiveness",
            "Condition",
            "Strategic\nSignificance",
            "Difficulty",
            "Time",
            "Units",
        ]
        parcels = [(self.baseline[p.baseline_pid], p) for p in self.enhanced.values()]
        # TODO: should check that areas match for created habitats with linked baseline
        creation_parcels = [
            (self.baseline[p.baseline_pid], p)
            for p in self.created.values()
            if p.baseline_pid is not None
        ]
        if len(creation_parcels) >= 1:
            parcels += creation_parcels

        data = [
            [
                " - ".join((b.pid, p.pid)),
                "\n - ".join((b.habitat, p.habitat)),
                " - ".join((b.distinctiveness.name, p.distinctiveness.name)),
                " - ".join((b.condition.name, p.condition.name)),
                " - ".join(
                    (b.strategic_significance.name, p.strategic_significance.name)
                ),
                p.enhancement_difficulty.name
                if p.pid in self.enhanced.keys()
                else p.creation_difficulty.name,
                f"{p.enhancement_time(b).time:g}y"
                if p.pid in self.enhanced.keys()
                else f"{p.creation_time.time:g}y",
                " - ".join(
                    (
                        f"{b.biodiversity_units:.2f}",
                        f"{p.enhancement_units(b):.2f}"
                        if p.pid in self.enhanced.keys()
                        else f"{p.creation_units:.2f}",
                    )
                ),
            ]
            for (b, p) in parcels
        ]
        return tabulate.tabulate(
            data, headers=headers, tablefmt=self.tablefmt, floatfmt=self.floatfmt
        )

    @property
    def summary_info(self) -> str:
        """Tabulate summary of Metric scores."""
        headers = [
            "",
            "Area",
            "Units",
        ]
        data = [
            ["Baseline", f"{self.baseline_area:.2f}", f"{self.baseline_units:.2f}"],
            [
                "Post-intervention",
                f"{self.post_intervention_area:.2f}",
                f"{self.post_intervention_units:.2f}",
            ],
            ["---Retained", f"{self.retained_area}", f"{self.retained_units:.2f}"],
            [
                "---Enhanced",
                f"{self.enhancement_area:.2f}",
                f"{self.enhancement_units:.2f}",
            ],
            ["---Created", f"{self.creation_area:.2f}", f"{self.creation_units:.2f}"],
            [
                "Change",
                f"{self.post_intervention_area - self.baseline_area:.2f}",
                rf"{self.post_intervention_units - self.baseline_units:.2f} ({self.metric_score:.2f}%)",
            ],
        ]
        return tabulate.tabulate(
            data, headers=headers, tablefmt=self.tablefmt, floatfmt=self.floatfmt
        )
