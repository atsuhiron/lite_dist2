import pytest

from lite_dist2.value_models.line_segment import (
    LineSegment,
    ParameterRangeBool,
    ParameterRangeFloat,
    ParameterRangeInt,
)


@pytest.mark.parametrize(
    ("one", "other", "expected"),
    [
        (  # complete match True
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            True,
        ),
        (  # different start True
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=16, ambient_size=255, start=10, step=1),
            True,
        ),
        (  # different size True
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=16, ambient_size=255, start=10, step=1),
            True,
        ),
        (  # different name False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeInt(name="y", type="int", size=100, ambient_index=16, ambient_size=255, start=10, step=1),
            False,
        ),
        (  # different type False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=True, step=1),
            False,
        ),
        (  # different ambient_size False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=16, ambient_size=16, start=10, step=1),
            False,
        ),
        (  # different step False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=16, ambient_size=255, start=10, step=2),
            False,
        ),
    ],
)
def test_line_segment_derived_by_same_ambient_space_with(one: LineSegment, other: LineSegment, expected: bool) -> None:
    actual = one.derived_by_same_ambient_space_with(other)
    actual_reverse = other.derived_by_same_ambient_space_with(one)
    assert actual == expected
    assert actual_reverse == expected


@pytest.mark.parametrize(
    ("one", "other", "expected"),
    [  # Cases that can be excluded by `derived_by_same_ambient_space_with` are not test here
        (  # complete match True
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
            True,
        ),
        (  # adjacency True
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=1, ambient_size=2, start=True),
            True,
        ),
        (  # complete match True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            True,
        ),
        (  # adjacency True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=10, ambient_size=255, start=10),
            True,
        ),
        (  # overlap True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=5, ambient_size=255, start=5),
            True,
        ),
        (  # stride False
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=11, ambient_size=255, start=11),
            False,
        ),
        (  # Complete match True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            True,
        ),
        (  # overlap True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=5, ambient_size=255, start=5.0, step=1),
            True,
        ),
        (  # adjacency True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=10, ambient_size=255, start=10.0, step=1),
            True,
        ),
        (  # stride False
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=11, ambient_size=255, start=11.0, step=1),
            False,
        ),
    ],
)
def test_line_segment_can_merge(one: LineSegment, other: LineSegment, expected: bool) -> None:
    actual = one.can_merge(other)
    actual_reverse = other.can_merge(one)
    assert actual == expected
    assert actual_reverse == expected
