import math
import random

from hypothesis import assume, given
from hypothesis.strategies import floats, sampled_from
import pytest

from metric import CONFIG
from metric.habitat import (
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
    area=floats(min_value=0, max_value=1e6),
)
def test_parcel_construction_and_typing(
    habitat, condition, strategic_significance, area
):
    """Test instantiation of HabitatParcel and correct typing of basic properties."""
    # parcel.creation_time raises TargetNotPossible if creation_time is None
    creation_time = CONFIG.habitats[habitat]["creation_time"][condition.name]
    assume(creation_time is not None)

    parcel = HabitatParcel(
        pid="test",
        habitat=habitat,
        condition=condition,
        strategic_significance=strategic_significance,
        area=area,
    )
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


@given(
    habitat=sampled_from(valid_habitats),
    condition=sampled_from(Condition),
    strategic_significance=sampled_from(StrategicSignificance),
    area=floats(min_value=0, max_value=1e6, exclude_min=True),
)
def test_positivity(habitat, condition, strategic_significance, area):
    """Check that biodiversity units are positive and nonzero for nonzero area,
    when the distinctiveness and condition scores are also nonzero."""
    parcel = HabitatParcel(
        pid="test",
        habitat=habitat,
        condition=condition,
        strategic_significance=strategic_significance,
        area=area,
    )
    assume(parcel.condition.value > 0 and parcel.distinctiveness.value > 0)
    assert parcel.biodiversity_units > 0


@given(habitat=sampled_from(valid_habitats), condition=sampled_from(Condition))
def test_target_not_possible_exception(habitat, condition):
    """Check that exception correctly raised if creation_time is None."""
    creation_time = CONFIG.habitats[habitat]["creation_time"][condition.name]
    assume(creation_time is None)

    parcel = HabitatParcel(
        pid="test",
        habitat=habitat,
        condition=condition,
        strategic_significance=random_strategic_significance(),
        area=1,
    )
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


@given(
    habitat=sampled_from(valid_habitats),
    condition=sampled_from(Condition),
    strategic_significance=sampled_from(StrategicSignificance),
    area=floats(min_value=0, max_value=1e6, exclude_min=True),
)
def test_creation_time_penalty(habitat, condition, strategic_significance, area):
    """Check that a time penalty is applied to created habitats."""
    # parcel.creation_time raises TargetNotPossible if creation_time is None
    creation_time = CONFIG.habitats[habitat]["creation_time"][condition.name]
    assume(creation_time is not None)

    parcel = HabitatParcel(
        pid="test",
        habitat=habitat,
        condition=condition,
        strategic_significance=strategic_significance,
        area=area,
    )
    assume(parcel.condition.value > 0 and parcel.distinctiveness.value > 0)
    assert parcel.creation_units < parcel.biodiversity_units


@pytest.mark.xfail(
    reason="Enhancement difficulty and time penalty can result in a decrease in biodiversity units, even when the condition/distinctiveness score increases"
)
@given(
    habitat_baseline=sampled_from(valid_habitats),
    condition_baseline=sampled_from(Condition),
    habitat_post=sampled_from(valid_habitats),
    condition_post=sampled_from(Condition),
)
def test_post_intervention(
    habitat_baseline, condition_baseline, habitat_post, condition_post
):
    """Check that valid post-intervention scenarios possess more biodiversity units
    than the baseline, but less that a penalty is applied for not-yet-existence."""
    strategic_significance = random_strategic_significance()
    baseline = HabitatParcel(
        pid="baseline",
        habitat=habitat_baseline,
        condition=condition_baseline,
        strategic_significance=strategic_significance,
        area=1,
    )
    enhanced = HabitatParcel(
        pid="enhanced",
        habitat=habitat_post,
        condition=condition_post,
        strategic_significance=strategic_significance,
        area=1,
    )

    assume(
        enhanced.distinctiveness.value + enhanced.condition.value
        > baseline.distinctiveness.value + baseline.condition.value
    )

    enhancement_units = None
    try:
        enhancement_units = enhanced.enhancement_units(baseline)
    except TargetNotPossible:
        pass
    assume(enhancement_units is not None)

    assert enhancement_units < enhanced.biodiversity_units

    # NOTE: this really ought to be true, but the difficulty and time penalty mean
    # it can be false for certain habitats. This is the kind of crap that emerges
    # when you pretend that uncertainty is a multiplicative factor.
    assert enhancement_units > baseline.biodiversity_units
