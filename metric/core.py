from enum import Enum
from types import SimpleNamespace
from typing import Optional

from fuzzywuzzy import process
from jsonargparse import ArgumentParser, namespace_to_dict
from jsonargparse.typing import final, PositiveInt, PositiveFloat

from metric import CONFIG, INPUTS


Distinctiveness = Enum("Distinctiveness", CONFIG.distinctiveness)
Condition = Enum("Condition", CONFIG.condition)
StrategicSignificance = Enum("StrategicSignificance", CONFIG.strategic_significance)
Difficulty = Enum("Difficulty", CONFIG.difficulty)
SpatialRisk = Enum("SpatialRisk", CONFIG.spatial_risk)


class TargetNotPossible(Exception):
    pass


class AreasNotEqual(Exception):
    pass


@final
class HabitatParcel:
    """Class representing a parcel of habitat with given coordinates or area.

    Args:
        pid: str
        habitat: str
        condition: Condition
        strategic_significance: StrategicSignificance
        area: PositiveFloat
        description: str (optional)
    """

    def __init__(
        self,
        *,
        pid: str,
        habitat: str,
        condition: Condition,
        strategic_significance: StrategicSignificance,
        area: PositiveFloat,
        description: Optional[str] = None,
    ):
        self._pid = pid
        self._condition = condition
        self._strategic_significance = strategic_significance
        self._area = area

        if description is not None:
            self._description = description

        # Extract closest match to valid habitat class
        self._habitat, _ = process.extractOne(
            query=habitat, choices=CONFIG.habitats.keys()
        )
        # Cache the habitat config for faster accessing
        self._habitat_config = SimpleNamespace(**CONFIG.habitats[self.habitat])

    @property
    def pid(self) -> str:
        """Unique identifier for this habitat parcel."""
        return self._pid

    @property
    def habitat(self) -> str:
        """Class label for this habitat."""
        return self._habitat

    @property
    def condition(self) -> Condition:
        """Condition category and score for habitat class."""
        return self._condition

    @property
    def strategic_significance(self) -> StrategicSignificance:
        """Strategic significance category and score for this habitat parcel."""
        return self._strategic_significance

    @property
    def area(self) -> float:
        """Area of this habitat parcel."""
        return self._area

    @property
    def distinctiveness(self) -> Distinctiveness:
        """Distinctiveness category and score for habitat class."""
        return getattr(Distinctiveness, self._habitat_config.distinctiveness)

    @property
    def creation_difficulty(self) -> Difficulty:
        """Creation difficulty category and score for habitat class."""
        return getattr(Difficulty, self._habitat_config.creation_difficulty)

    @property
    def enhancement_difficulty(self) -> Difficulty:
        """Enhancement difficulty category and score for habitat class."""
        return getattr(Difficulty, self._habitat_config.enhancement_difficulty)

    @property
    def creation_time(self) -> PositiveInt:
        """Time (years) required to create habitat class in given condition.

        Raises:
            TargetNotPossible: If configuration does not permit creation of this
                habitat class in the given condition.
        """
        time = self._habitat_config.creation_time[self.condition.name]
        if time == None:
            raise TargetNotPossible(
                f"Configuration does not permit creation of habitat class: {self.habitat} in condition: {self.condition.name}."
            )
        return int(time)

    @property
    def biodiversity_units(self) -> PositiveFloat:
        """Biodiversity Units attributed to this habitat parcel, given its existence."""
        return (
            self.area
            * self.distinctiveness.value
            * self.condition.value
            * self.strategic_significance.value
        )

    @property
    def creation_units(self) -> PositiveFloat:
        """Biodiversity Units awarded for proposed creation of this habitat parcel."""
        return (
            self.biodiversity_units
            * self.creation_difficulty.value
            * pow(1 - CONFIG.depreciation / 100, self.creation_time)
        )


@final
class EnhancedHabitatParcel(HabitatParcel):
    """Extension of `HabitatParcel` for 'enhancement' scenarios.

    Takes an additional argument `baseline_pid` which must match the corresponding `pid`
    for the baseline habitat parcel, which must have the same area.

    Args:
        pid: str
        baseline_pid: str
        habitat: str
        condition: Condition
        strategic_significance: StrategicSignificance
        area: PositiveFloat
        description: str (optional)
    """
        
    def __init__(
        self,
        *,
        pid: str,
        baseline_pid: str,
        habitat: str,
        condition: Condition,
        strategic_significance: StrategicSignificance,
        area: PositiveFloat,
        description: Optional[str] = None,
    ):
        super().__init__(
            pid=pid,
            habitat=habitat,
            condition=condition,
            strategic_significance=strategic_significance,
            area=area,
            description=description,
        )
        self._baseline_pid = baseline_pid

    @property
    def baseline_pid(self):
        """Unique identifier for the corresponding baseline parcel."""
        return self._baseline_pid

    def enhancement_time(self, baseline: "HabitatParcel") -> PositiveInt:
        """Time (years) required to enhance a 'baseline' habitat to reach given
        habitat class and condition.

        Args:
            baseline: HabitatParcel
                Object representing the current state of the habitat parcel.

        Raises:
            TargetNotPossible: If configuration does not permit enhancement of
            `baseline` up to the given habitat class in the given condition.
        """
        if abs(baseline.area - self.area) > 1e-3:
            raise AreasNotEqual(
                f"Area of baseline: {baseline.area} does not match area of enhancement: {self.area}"
            )

        if baseline.distinctiveness.value < self.distinctiveness.value:
            key = f"Lower Distinctiveness Habitat - {self.condition.name}"
        else:
            key = f"{baseline.condition.name} - {self.condition.name}"

        time = self._habitat_config.enhancement_time[key]
        if time == None:
            raise TargetNotPossible(
                f"Configuration does not permit enhancement: {key} for habitat class: {self.habitat}."
            )
        return int(time)

    def enhancement_units(self, baseline: "HabitatParcel") -> PositiveFloat:
        """Biodiversity Units awarded for proposed enhancement of `baseline` habitat
        (of the same area) to reach the given habitat parcel.

        Args:
            baseline: HabitatParcel
                Object representing the current state of the habitat parcel.
        """
        return (
            self.biodiversity_units
            * self.enhancement_difficulty.value
            * pow(1 - CONFIG.depreciation / 100, self.enhancement_time(baseline))
        )


def load_scenario() -> SimpleNamespace:
    """Instantiates `HabitatParcel`s based on provided information.

    Returns namespace containing three elements
        - baseline
        - creation
        - enhancement

    Each element is a dict of `HabitatParcel` objects indexed by their (hopefully
    unique) parcel id (`HabitatParcel.pid`).
    """

    parser = ArgumentParser()
    parser.add_argument("--baseline", type=HabitatParcel, nargs="+")
    parser.add_argument("--creation", type=HabitatParcel, nargs="+")
    parser.add_argument("--enhancement", type=EnhancedHabitatParcel, nargs="+")

    scenario = {}
    for infile in INPUTS:
        scenario.update(
            {
                k: {
                    parcel["pid"]: EnhancedHabitatParcel(**parcel)
                    if k == "enhancement"
                    else HabitatParcel(**parcel)
                    for parcel in v
                }
                for k, v, in namespace_to_dict(parser.parse_path(infile)).items()
                if v is not None
            }
        )

    return SimpleNamespace(**scenario)
