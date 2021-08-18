from collections import namedtuple
import json
from types import SimpleNamespace

from fuzzywuzzy import process
from jsonargparse.typing import final, PositiveInt, PositiveFloat

from metric.typing import (
    Distinctiveness,
    Condition,
    StrategicSignificance,
    Difficulty,
    SpatialRisk,
)

with open("config.json", "r") as fp:
    config = SimpleNamespace(**json.load(fp))


class TargetNotPossible(Exception):
    pass


@final
class HabitatParcel:
    """Class representing a parcel of habitat with given coordinates or area.

    Args:
        habitat: str
        condition: str
        strategic_significance: str
        area: float
        description: str (optional)
    """

    def __init__(
        self,
        parcel_id: str,
        habitat: str,
        condition: Condition,
        strategic_significance: StrategicSignificance,
        area: PositiveFloat,
        description: str = "",
    ):
        self._habitat_class, _ = process.extractOne(
            query=habitat, choices=config.habitats.keys()
        )
        habitat = SimpleNamespace(**config.habitats[self._habitat_class])

        self._distinctiveness = getattr(Distinctiveness, habitat.distinctiveness)
        self._condition = condition
        self._strategic_significance = strategic_significance
        self._creation_difficulty = getattr(Difficulty, habitat.creation_difficulty)
        self._enhancement_difficulty = getattr(
            Difficulty, habitat.enhancement_difficulty
        )
        self._creation_time = habitat.creation_time[condition.name]
        self._habitat = habitat
        self._area = area

        """
        NumberedCategory(
            properties.distinctiveness,
            config.distinctiveness[properties.distinctiveness],
        )
        self._creation_difficulty = NumberedCategory(
            properties.creation_difficulty,
            config.difficulty[properties.creation_difficulty],
        )
        self._enhancement_difficulty = NumberedCategory(
            properties.enhancement_difficulty,
            config.difficulty[properties.enhancement_difficulty],
        )
        self._condition = NumberedCategory(condition, config.condition[condition])
        self._strategic_significance = NumberedCategory(
            strategic_significance,
            config.strategic_significance[strategic_significance],
        )
        self._creation_time = properties.creation_time[condition]
        """

    @property
    def area(self) -> float:
        """Area of this habitat parcel."""
        return self._area

    @property
    def distinctiveness(self) -> Distinctiveness:
        """Distinctiveness category and score for habitat class."""
        return self._distinctiveness

    @property
    def condition(self) -> Condition:
        """Condition category and score for habitat class."""
        return self._condition

    @property
    def strategic_significance(self) -> StrategicSignificance:
        """Strategic significance category and score for this habitat parcel."""
        return self._strategic_significance

    @property
    def creation_difficulty(self) -> Difficulty:
        """Creation difficulty category and score for habitat class."""
        return self._creation_difficulty

    @property
    def enhancement_difficulty(self) -> Difficulty:
        """Enhancement difficulty category and score for habitat class."""
        return self._enhancement_difficulty

    @property
    def creation_time(self) -> PositiveInt:
        """Time (years) required to create habitat class in given condition.

        Raises:
            TargetNotPossible: If configuration does not permit creation of this
                habitat class in the given condition.
        """
        if self._creation_time == "Not Possible":
            raise TargetNotPossible(
                f"Configuration does not permit creation of habitat class: {self.habitat} in condition: {self.condition.name}."
            )
        return int(self._creation_time)

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
            # raise AreasNotEqual
            pass

        if baseline.distinctiveness.value < self.distinctiveness.value:
            key = f"Lower Distinctiveness Habitat - {self.condition.name}"
        else:
            key = f"{baseline.condition.name} - {self.condition.name}"

        time = self._habitat_properties.enhancement_time[key]

        if time == "Not Possible":
            raise TargetNotPossible(
                f"Configuration does not permit enhancement: {key} for habitat class: {self.habitat}."
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
            * pow(1 - config.depreciation / 100, self.creation_time)
        )

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
            * pow(1 - config.depreciation / 100, self.enhancement_time(baseline))
        )
