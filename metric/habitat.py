from enum import Enum
from types import SimpleNamespace
from typing import Optional, TypedDict

from fuzzywuzzy import process
from jsonargparse.typing import final, PositiveFloat

from metric import CONFIG


Distinctiveness = Enum("Distinctiveness", CONFIG.distinctiveness)
Condition = Enum("Condition", CONFIG.condition)
StrategicSignificance = Enum("StrategicSignificance", CONFIG.strategic_significance)
Difficulty = Enum("Difficulty", CONFIG.difficulty)
SpatialRisk = Enum("SpatialRisk", CONFIG.spatial_risk)


class HabitatParcelInput(TypedDict):
    pid: str
    habitat: str
    condition: Condition
    strategic_significance: StrategicSignificance
    area: PositiveFloat
    description: Optional[str]
    baseline_pid: Optional[str]


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
        condition: str
        strategic_significance: str
        area: PositiveFloat
        baseline_pid: Optional[str]
        description: Optional[str]
    """

    def __init__(
        self,
        *,
        pid: str,
        habitat: str,
        condition: Condition,
        strategic_significance: StrategicSignificance,
        area: PositiveFloat,
        baseline_pid: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self._pid = pid
        self._condition = condition
        self._strategic_significance = strategic_significance
        self._area = area

        if baseline_pid is not None:
            self._baseline_pid = baseline_pid
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
    def baseline_pid(self) -> str:
        """Unique identifier for the corresponding baseline parcel (enhancement only)."""
        # Hopefully raising AttributeError is transparent enough when called erronesously
        return self._baseline_pid

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
    def creation_time(self) -> float:
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
        return float(time)

    @property
    def biodiversity_units(self) -> float:
        """Biodiversity Units attributed to this habitat parcel, given its existence."""
        return (
            self.area
            * self.distinctiveness.value
            * self.condition.value
            * self.strategic_significance.value
        )

    @property
    def creation_units(self) -> float:
        """Biodiversity Units awarded for proposed creation of this habitat parcel."""
        return (
            self.biodiversity_units
            * self.creation_difficulty.value
            * pow(1 - float(CONFIG.depreciation) / 100, self.creation_time)
        )

    def enhancement_time(self, baseline: "HabitatParcel") -> float:
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
        return float(time)

    def enhancement_units(self, baseline: "HabitatParcel") -> float:
        """Biodiversity Units awarded for proposed enhancement of `baseline` habitat
        (of the same area) to reach the given habitat parcel.

        Args:
            baseline: HabitatParcel
                Object representing the current state of the habitat parcel.
        """
        return (
            self.biodiversity_units
            * self.enhancement_difficulty.value
            * pow(1 - float(CONFIG.depreciation) / 100, self.enhancement_time(baseline))
        )
