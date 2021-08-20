from typing import Optional

import jsonargparse

from metric.habitat import HabitatParcel, HabitatParcelInput


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
    def baseline_units(self) -> float:
        """Total Biodiversity Units from the baseline habitats."""
        return sum([parcel.biodiversity_units for parcel in self._baseline.values()])

    @property
    def retained_units(self) -> float:
        """Total Biodiversity Units from the retained habitats."""
        return sum([self._baseline[pid].biodiversity_units for pid in self._retained])

    @property
    def creation_units(self) -> float:
        """Total Biodiversity Units from the created habitats."""
        return sum([parcel.creation_units for parcel in self._created.values()])

    @property
    def enhancement_units(self) -> float:
        """Total Biodiversity Units from the enhanced habitats."""
        return sum(
            [
                parcel.enhancement_units(self._baseline[parcel.baseline_pid])
                for parcel in self._enhanced.values()
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
