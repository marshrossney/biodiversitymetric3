import math
import random

from hypothesis import assume, given
from hypothesis.strategies import just, floats, sampled_from
import jsonargparse
import pytest

from metric import CONFIG
from metric.habitat import (
    HabitatParcelInput,
    Distinctiveness,
    Condition,
    StrategicSignificance,
    Difficulty,
    SpatialRisk,
    TimePenalty,
    TargetNotPossible,
    AreasNotEqual,
    HabitatParcel,
)

valid_habitats = list(CONFIG.habitats.keys())

random_habitat = lambda: random.choice(valid_habitats)
random_condition = lambda: random.choice(list(Condition))
random_strategic_significance = lambda: random.choice(list(StrategicSignificance))


@given(
    habitat=sampled_from(valid_habitats),
    condition=sampled_from(Condition),
    strategic_significance=sampled_from(StrategicSignificance),
    area=floats(min_value=0.0, allow_infinity=False),
)
def test_parcel_construction_and_typing(
    habitat, condition, strategic_significance, area
):
    """Test instantiation of HabitatParcel and correct typing of basic properties."""
    parcel = HabitatParcel(
        pid="test",
        habitat=habitat,
        condition=condition,
        strategic_significance=strategic_significance,
        area=area,
    )

    # parcel.creation_time raises TargetNotPossible if creation_time is None
    creation_time = CONFIG.habitats[habitat]["creation_time"][condition.name]
    assume(creation_time is not None)

    assert type(parcel.distinctiveness) is Distinctiveness
    assert type(parcel.condition) is Condition
    assert type(parcel.strategic_significance) is StrategicSignificance
    assert type(parcel.area) is float
    assert type(parcel.creation_difficulty) is Difficulty
    assert type(parcel.enhancement_difficulty) is Difficulty
    assert type(parcel.creation_time) is TimePenalty
    assert type(parcel.biodiversity_units) is float
    assert type(parcel.creation_units) is float


def test_null_area():
    """Check that a habitat parcel with area=0 has 0 biodiversity units."""
    parcel = HabitatParcel(
        pid="test",
        habitat=random_habitat(),
        condition=random_condition(),
        strategic_significance=random_strategic_significance(),
        area=0,
    )

    assert math.isclose(parcel.area, 0)
    assert math.isclose(parcel.biodiversity_units, 0)


@given(habitat=sampled_from(valid_habitats), condition=sampled_from(Condition))
def test_target_not_possible_exception(habitat, condition):
    """Check that exception correctly raised if creation_time is None."""
    parcel = HabitatParcel(
        pid="test",
        habitat=habitat,
        condition=condition,
        strategic_significance=random_strategic_significance(),
        area=1,
    )
    creation_time = CONFIG.habitats[habitat]["creation_time"][condition.name]
    assume(creation_time is None)

    with pytest.raises(TargetNotPossible):
        _ = parcel.creation_time


def test_areas_not_equal_exception():
    """Check that exception correctly raised if area of enhanced parcel not
    equal to area of baseline parcel."""
    baseline = HabitatParcel(
        pid="baseline",
        habitat=random_habitat(),
        condition=random_condition(),
        strategic_significance=random_strategic_significance(),
        area=1,
    )
    enhanced = HabitatParcel(
        pid="enhanced",
        habitat=random_habitat(),
        condition=random_condition(),
        strategic_significance=random_strategic_significance(),
        area=2,
    )

    # NOTE: Assumes that area equality checked before validity of enhancement!
    with pytest.raises(AreasNotEqual):
        _ = enhanced.enhancement_time(baseline)
