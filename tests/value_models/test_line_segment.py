import pytest

from lite_dist2.common import hex2float
from lite_dist2.value_models.line_segment import (
    LineSegment,
    LineSegmentModel,
    ParameterRangeBool,
    ParameterRangeFloat,
    ParameterRangeInt,
)


@pytest.mark.parametrize(
    ("seg", "expected"),
    [
        (ParameterRangeBool(type="bool", size=1, ambient_index=0, ambient_size=2, start=False), 0),
        (ParameterRangeBool(type="bool", size=1, ambient_index=1, ambient_size=1, start=True), 1),
        (ParameterRangeInt(type="int", size=10, ambient_index=0, ambient_size=255, start=0), 9),
        (ParameterRangeInt(type="int", size=10, ambient_index=5, ambient_size=255, start=0), 14),
        (ParameterRangeFloat(type="float", size=5, ambient_index=0, ambient_size=255, start=11, step=1), 4),
        (ParameterRangeFloat(type="float", size=5, ambient_index=2, ambient_size=255, start=11, step=1), 6),
    ],
)
def test_line_segment_end_index(seg: LineSegment, expected: int) -> None:
    actual = seg.end_index()
    assert actual == expected


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


@pytest.mark.parametrize(
    ("one", "other", "expected"),
    [
        (  # complete match True
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
        ),
        (  # adjacency True
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=1, ambient_size=2, start=True),
            ParameterRangeBool(name="x", type="bool", size=2, ambient_index=0, ambient_size=2, start=False),
        ),
        (  # complete match True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
        ),
        (  # adjacency True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=10, ambient_size=255, start=10),
            ParameterRangeInt(name="x", type="int", size=20, ambient_index=0, ambient_size=255, start=0),
        ),
        (  # overlap True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size=255, start=0),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=5, ambient_size=255, start=5),
            ParameterRangeInt(name="x", type="int", size=15, ambient_index=0, ambient_size=255, start=0),
        ),
        (  # Complete match True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
        ),
        (  # overlap True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=5, ambient_size=255, start=5.0, step=1),
            ParameterRangeFloat(type="float", size=15, ambient_index=0, ambient_size=255, start=0.0, step=1),
        ),
        (  # adjacency True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=10, ambient_size=255, start=10.0, step=1),
            ParameterRangeFloat(type="float", size=20, ambient_index=0, ambient_size=255, start=0.0, step=1),
        ),
    ],
)
def test_line_segment_merge(one: LineSegment, other: LineSegment, expected: LineSegment) -> None:
    actual = one.merge(other)
    actual_reverse = other.merge(one)
    assert actual == expected
    assert actual_reverse == expected


@pytest.mark.parametrize(
    ("line_segment", "expected"),
    [
        (ParameterRangeBool(type="bool", size=1, ambient_index=0, ambient_size=1, start=False), True),
        (ParameterRangeBool(type="bool", size=2, ambient_index=0, ambient_size=2, start=False), True),
        (ParameterRangeBool(type="bool", size=1, ambient_index=0, ambient_size=2, start=True), False),
        (ParameterRangeInt(type="int", size=10, ambient_index=0, ambient_size=100, start=0), False),
        (ParameterRangeInt(type="int", size=10, ambient_index=0, ambient_size=10, start=0), True),
        (ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=100, start=0, step=2.0), False),
        (ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size=10, start=0, step=2.0), True),
    ],
)
def test_line_segment_is_universal(line_segment: LineSegment, expected: bool) -> None:
    actual = line_segment.is_universal()
    assert actual == expected


@pytest.mark.parametrize(
    ("line_segment", "start_index", "size", "expected"),
    [
        (
            ParameterRangeBool(name="x", type="bool", size=2, ambient_index=0, ambient_size=2, start=False),
            0,
            1,
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
        ),
        (
            ParameterRangeBool(name="x", type="bool", size=2, ambient_index=0, ambient_size=2, start=False),
            1,
            1,
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=1, ambient_size=2, start=True),
        ),
        (
            ParameterRangeInt(type="int", size=10, ambient_index=20, ambient_size=100, start=20, step=1),
            5,
            4,
            ParameterRangeInt(type="int", size=4, ambient_index=25, ambient_size=100, start=25, step=1),
        ),
        (
            ParameterRangeFloat(type="float", size=10, ambient_index=20, ambient_size=100, start=-100.0, step=5.0),
            5,
            4,
            ParameterRangeFloat(type="float", size=4, ambient_index=25, ambient_size=100, start=-75.0, step=5.0),
        ),
    ],
)
def test_line_segment_slice(line_segment: LineSegment, start_index: int, size: int, expected: LineSegment) -> None:
    actual = line_segment.slice(start_index, size)
    assert actual == expected


@pytest.mark.parametrize(
    "model",
    [
        LineSegmentModel(name="x", type="bool", size=2, step=1, start=False, ambient_index="0x0", ambient_size="0x2"),
        LineSegmentModel(type="bool", size=2, step=1, start=False, ambient_index="0x0", ambient_size="0x2"),
    ],
)
def test_line_segment_model_bool_to_model_from_model(model: LineSegmentModel) -> None:
    segment = ParameterRangeBool.from_model(model)
    reconstructed_model = segment.to_model()
    assert model == reconstructed_model


@pytest.mark.parametrize(
    "model",
    [
        LineSegmentModel(name="x", type="int", size=10, step=1, start="0x0", ambient_index="0x0", ambient_size="0x64"),
        LineSegmentModel(type="int", size=10, step=1, start="0x0", ambient_index="0x0", ambient_size="0x64"),
    ],
)
def test_line_segment_model_int_to_model_from_model(model: LineSegmentModel) -> None:
    segment = ParameterRangeInt.from_model(model)
    reconstructed_model = segment.to_model()
    assert model == reconstructed_model


@pytest.mark.parametrize(
    "model",
    [
        LineSegmentModel(
            name="x",
            type="float",
            size=10,
            step="0x1.0p-1",
            start="0x0.0p+0",
            ambient_index="0x0",
            ambient_size="0x64",
        ),
        LineSegmentModel(
            type="float",
            size=10,
            step="0x1.0p-1",
            start="0x0.0p+0",
            ambient_index="0x0",
            ambient_size="0x64",
        ),
    ],
)
def test_line_segment_model_float_to_model_from_model(model: LineSegmentModel) -> None:
    segment = ParameterRangeFloat.from_model(model)
    reconstructed_model = segment.to_model()
    assert model.name == reconstructed_model.name
    assert model.type == reconstructed_model.type
    assert model.size == reconstructed_model.size
    assert model.ambient_index == reconstructed_model.ambient_index
    assert model.ambient_size == reconstructed_model.ambient_size
    assert hex2float(model.start) == hex2float(reconstructed_model.start)
    assert hex2float(model.step) == hex2float(reconstructed_model.step)
