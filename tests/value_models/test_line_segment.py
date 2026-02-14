from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from lite_dist2.common import hex2float
from lite_dist2.expections import LD2ParameterError
from lite_dist2.value_models.line_segment import LineSegment, LineSegmentPortableModel

if TYPE_CHECKING:
    from lite_dist2.type_definitions import PrimitiveValueType


@pytest.mark.parametrize(
    ("seg", "expected"),
    [
        (LineSegment(name="x", type_="bool", size=1, step=True, ambient_index=0, ambient_size=2, start=False), 0),
        (LineSegment(name="y", type_="bool", size=1, step=True, ambient_index=1, ambient_size=1, start=True), 1),
        (LineSegment(name="z", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=255), 9),
        (LineSegment(name="w", type_="int", size=10, step=1, start=0, ambient_index=5, ambient_size=255), 14),
        (LineSegment(name="a", type_="float", size=5, step=1.0, start=11, ambient_index=0, ambient_size=255), 4),
        (LineSegment(name="b", type_="float", size=5, step=1.0, start=11, ambient_index=2, ambient_size=255), 6),
    ],
)
def test_line_segment_end_index(seg: LineSegment, expected: int) -> None:
    actual = seg.end_index()
    assert actual == expected


@pytest.mark.parametrize(
    ("one", "other", "expected"),
    [
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            True,
            id="complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="x", type_="int", size=100, ambient_index=16, ambient_size=255, start=10, step=1),
            True,
            id="different start True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="x", type_="int", size=10, ambient_index=16, ambient_size=255, start=10, step=1),
            True,
            id="different size True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="y", type_="int", size=100, ambient_index=16, ambient_size=255, start=10, step=1),
            False,
            id="different name False",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="x", type_="bool", size=1, ambient_index=0, ambient_size=2, start=True, step=1),
            False,
            id="different type False",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="x", type_="int", size=100, ambient_index=16, ambient_size=16, start=10, step=1),
            False,
            id="different ambient_size False",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=100, ambient_index=0, ambient_size=255, start=0, step=1),
            LineSegment(name="x", type_="int", size=100, ambient_index=16, ambient_size=255, start=10, step=2),
            False,
            id="different step False",
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
        pytest.param(
            LineSegment(name="x", type_="bool", size=1, step=True, ambient_index=0, ambient_size=2, start=False),
            LineSegment(name="x", type_="bool", size=1, step=True, ambient_index=0, ambient_size=2, start=False),
            True,
            id="bool: complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="bool", size=1, step=True, ambient_index=0, ambient_size=2, start=False),
            LineSegment(name="x", type_="bool", size=1, step=True, ambient_index=1, ambient_size=2, start=True),
            True,
            id="bool: adjacency True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=0, ambient_size=255, start=0),
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=0, ambient_size=255, start=0),
            True,
            id="int: complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=0, ambient_size=255, start=0),
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=10, ambient_size=255, start=10),
            True,
            id="int: adjacency True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=0, ambient_size=255, start=0),
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=5, ambient_size=255, start=5),
            True,
            id="int: overlap True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=0, ambient_size=255, start=0),
            LineSegment(name="x", type_="int", size=10, step=1, ambient_index=11, ambient_size=255, start=11),
            False,
            id="int: stride False",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            True,
            id="float: complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=5, ambient_size=255, start=5.0, step=1),
            True,
            id="float: overlap True",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=10, ambient_size=255, start=10.0, step=1),
            True,
            id="float: adjacency True",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=11, ambient_size=255, start=11.0, step=1),
            False,
            id="float: stride False",
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
        pytest.param(
            LineSegment(name="x", type_="bool", size=1, step=True, start=False, ambient_index=0, ambient_size=2),
            LineSegment(name="x", type_="bool", size=1, step=True, start=False, ambient_index=0, ambient_size=2),
            LineSegment(name="x", type_="bool", size=1, step=True, start=False, ambient_index=0, ambient_size=2),
            id="bool: complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="bool", size=1, step=True, start=False, ambient_index=0, ambient_size=2),
            LineSegment(name="x", type_="bool", size=1, step=True, start=True, ambient_index=1, ambient_size=2),
            LineSegment(name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
            id="bool: adjacency True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=255),
            LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=255),
            LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=255),
            id="int: complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=255),
            LineSegment(name="x", type_="int", size=10, step=1, start=10, ambient_index=10, ambient_size=255),
            LineSegment(name="x", type_="int", size=20, step=1, start=0, ambient_index=0, ambient_size=255),
            id="int: adjacency True",
        ),
        pytest.param(
            LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=255),
            LineSegment(name="x", type_="int", size=10, step=1, start=5, ambient_index=5, ambient_size=255),
            LineSegment(name="x", type_="int", size=15, step=1, start=0, ambient_index=0, ambient_size=255),
            id="int: overlap True",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            id="float: complete match True",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, ambient_index=0, ambient_size=255, start=0.0, step=1),
            LineSegment(name="x", type_="float", size=10, ambient_index=5, ambient_size=255, start=5.0, step=1),
            LineSegment(name="x", type_="float", size=15, ambient_index=0, ambient_size=255, start=0.0, step=1),
            id="float: overlap True",
        ),
        pytest.param(
            LineSegment(name="x", type_="float", size=10, step=1.0, start=0.0, ambient_index=0, ambient_size=255),
            LineSegment(name="x", type_="float", size=10, step=1.0, start=10.0, ambient_index=10, ambient_size=255),
            LineSegment(name="x", type_="float", size=20, step=1.0, start=0.0, ambient_index=0, ambient_size=255),
            id="float: adjacency True",
        ),
    ],
)
def test_line_segment_merge(one: LineSegment, other: LineSegment, expected: LineSegment) -> None:
    actual = one.merge(other)
    actual_reverse = other.merge(one)
    assert actual.to_model() == expected.to_model()
    assert actual_reverse.to_model() == expected.to_model()


@pytest.mark.parametrize(
    ("line_segment", "expected"),
    [
        (LineSegment(name="x", type_="bool", size=1, step=True, start=False, ambient_index=0, ambient_size=1), True),
        (LineSegment(name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2), True),
        (LineSegment(name="x", type_="bool", size=1, step=True, start=True, ambient_index=0, ambient_size=2), False),
        (LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=100), False),
        (LineSegment(name="x", type_="int", size=10, step=1, start=0, ambient_index=0, ambient_size=10), True),
        (LineSegment(name="x", type_="float", size=10, step=2.0, ambient_index=0, ambient_size=100, start=0.0), False),
        (LineSegment(name="x", type_="float", size=10, step=2.0, ambient_index=0, ambient_size=10, start=0.0), True),
    ],
)
def test_line_segment_is_universal(line_segment: LineSegment, expected: bool) -> None:
    actual = line_segment.is_universal()
    assert actual == expected


@pytest.mark.parametrize(
    ("line_segment", "start_index", "size", "expected"),
    [
        (
            LineSegment[bool](name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
            0,
            1,
            LineSegment[bool](name="x", type_="bool", size=1, step=True, start=False, ambient_index=0, ambient_size=2),
        ),
        (
            LineSegment[bool](name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
            1,
            1,
            LineSegment[bool](name="x", type_="bool", size=1, step=True, start=True, ambient_index=1, ambient_size=2),
        ),
        (
            LineSegment[bool](name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
            0,
            2,
            LineSegment[bool](name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
        ),
        (
            LineSegment(name="x", type_="int", size=10, step=1, start=20, ambient_index=20, ambient_size=100),
            5,
            4,
            LineSegment(name="x", type_="int", size=4, step=1, start=25, ambient_index=25, ambient_size=100),
        ),
        (
            LineSegment(name="x", type_="int", size=10, step=1, start=20, ambient_index=20, ambient_size=100),
            0,
            10,
            LineSegment(name="x", type_="int", size=10, step=1, start=20, ambient_index=20, ambient_size=100),
        ),
        (
            LineSegment(name="x", type_="float", size=10, step=5.0, start=-100.0, ambient_index=20, ambient_size=100),
            5,
            4,
            LineSegment(name="x", type_="float", size=4, step=5.0, start=-75.0, ambient_index=25, ambient_size=100),
        ),
        (
            LineSegment(name="x", type_="float", size=10, step=5.0, start=-100.0, ambient_index=20, ambient_size=100),
            0,
            10,
            LineSegment(name="x", type_="float", size=10, step=5.0, start=-100.0, ambient_index=20, ambient_size=100),
        ),
    ],
)
def test_line_segment_slice(line_segment: LineSegment, start_index: int, size: int, expected: LineSegment) -> None:
    actual = line_segment.slice(start_index, size)
    assert actual.to_model() == expected.to_model()


@pytest.mark.parametrize(
    ("line_segment", "size"),
    [
        pytest.param(
            LineSegment(name="x", type_="bool", size=2, step=True, ambient_index=0, ambient_size=2, start=False),
            3,
        ),
        pytest.param(
            LineSegment(name="y", type_="int", size=10, step=1, ambient_index=20, ambient_size=100, start=20),
            11,
        ),
        pytest.param(
            LineSegment(name="z", type_="float", size=10, step=5.0, ambient_index=20, ambient_size=100, start=-100.0),
            11,
        ),
    ],
)
def test_line_segment_slice_raise(line_segment: LineSegment, size: int) -> None:
    start_index = 0
    with pytest.raises(LD2ParameterError):
        _ = line_segment.slice(start_index, size)


@pytest.mark.parametrize(
    ("line_segment", "expected"),
    [
        pytest.param(
            LineSegment(name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
            [False, True],
            id="bool",
        ),
        pytest.param(
            LineSegment(name="y", type_="int", size=10, step=1, start=20, ambient_index=40, ambient_size=100),
            [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
            id="int",
        ),
        pytest.param(
            LineSegment(name="z", type_="float", size=5, step=0.5, start=20.0, ambient_index=40, ambient_size=100),
            [20.0, 20.5, 21.0, 21.5, 22.0],
            id="float",
        ),
    ],
)
def test_line_segment_grid_finite(line_segment: LineSegment, expected: list[PrimitiveValueType]) -> None:
    actual = list(line_segment.grid())
    assert actual == expected


@pytest.mark.parametrize(
    ("line_segment", "max_num", "expected"),
    [
        pytest.param(
            LineSegment(name="x", type_="int", size=None, ambient_index=20, ambient_size=None, start=20, step=1),
            5,
            [20, 21, 22, 23, 24],
            id="int",
        ),
        pytest.param(
            LineSegment(name="y", type_="float", size=None, ambient_index=40, ambient_size=None, start=20.0, step=0.5),
            5,
            [20.0, 20.5, 21.0, 21.5, 22.0],
            id="float",
        ),
    ],
)
def test_line_segment_grid_infinite(
    line_segment: LineSegment,
    max_num: int,
    expected: list[PrimitiveValueType],
) -> None:
    actual = []
    for item in line_segment.grid():
        actual.append(item)
        if len(actual) >= max_num:
            break
    assert actual == expected


@pytest.mark.parametrize(
    ("line_segment", "expected"),
    [
        pytest.param(
            LineSegment(name="x", type_="bool", size=2, step=True, start=False, ambient_index=0, ambient_size=2),
            [(0, False), (1, True)],
            id="bool",
        ),
        pytest.param(
            LineSegment(name="y", type_="int", size=10, step=1, start=20, ambient_index=40, ambient_size=100),
            [(40, 20), (41, 21), (42, 22), (43, 23), (44, 24), (45, 25), (46, 26), (47, 27), (48, 28), (49, 29)],
            id="int",
        ),
        pytest.param(
            LineSegment(name="z", type_="float", size=5, step=0.5, start=20.0, ambient_index=40, ambient_size=100),
            [(40, 20.0), (41, 20.5), (42, 21.0), (43, 21.5), (44, 22.0)],
            id="float",
        ),
    ],
)
def test_line_segment_indexed_grid_finite(
    line_segment: LineSegment,
    expected: list[tuple[int, PrimitiveValueType]],
) -> None:
    actual = list(line_segment.indexed_grid())
    assert actual == expected


@pytest.mark.parametrize(
    ("line_segment", "max_num", "expected"),
    [
        pytest.param(
            LineSegment(name="x", type_="int", size=None, ambient_index=40, ambient_size=None, start=20, step=1),
            5,
            [(40, 20), (41, 21), (42, 22), (43, 23), (44, 24)],
            id="int",
        ),
        pytest.param(
            LineSegment(name="y", type_="float", size=None, ambient_index=40, ambient_size=None, start=20.0, step=0.5),
            5,
            [(40, 20.0), (41, 20.5), (42, 21.0), (43, 21.5), (44, 22.0)],
            id="float",
        ),
    ],
)
def test_line_segment_indexed_grid_infinite(
    line_segment: LineSegment,
    max_num: int,
    expected: list[tuple[int, PrimitiveValueType]],
) -> None:
    actual = []
    for item in line_segment.indexed_grid():
        actual.append(item)
        if len(actual) >= max_num:
            break
    assert actual == expected


def test_line_segment_grid_without_rounding_error() -> None:
    ambient = LineSegment(
        name="x",
        type_="float",
        size=13,
        step=0.5 / 13,
        start=-0.25,
        ambient_index=0,
        ambient_size=13,
    )
    ambient_grid = list(ambient.grid())

    derived = LineSegment(
        name="x",
        type_="float",
        size=6,
        step=0.5 / 13,
        start=0.5 / 13 * 7 - 0.25,
        ambient_index=7,
        ambient_size=13,
    )
    derived_grid = list(derived.grid())

    amb_idx = 7
    assert len(ambient_grid[amb_idx:]) == len(derived_grid)
    for i in range(5):
        assert pytest.approx(ambient_grid[i + amb_idx]) == derived_grid[i]


@pytest.mark.parametrize(
    "model",
    [
        LineSegmentPortableModel(
            name="x",
            type="bool",
            size="0x2",
            step=True,
            start=False,
            ambient_index="0x0",
            ambient_size="0x2",
        ),
        LineSegmentPortableModel(
            type="bool",
            size="0x2",
            step=True,
            start=False,
            ambient_index="0x0",
            ambient_size="0x2",
        ),
    ],
)
def test_line_segment_model_bool_to_model_from_model(model: LineSegmentPortableModel) -> None:
    segment = model.to_line_segment_model()
    reconstructed_model = LineSegmentPortableModel.from_line_segment_model(segment)
    assert model == reconstructed_model


@pytest.mark.parametrize(
    "model",
    [
        LineSegmentPortableModel(
            name="x",
            type="int",
            size="0xa",
            step="0x1",
            start="0x0",
            ambient_index="0x0",
            ambient_size="0x64",
        ),
        LineSegmentPortableModel(
            type="int",
            size="0xa",
            step="0x1",
            start="0x0",
            ambient_index="0x0",
            ambient_size="0x64",
        ),
    ],
)
def test_line_segment_model_int_to_model_from_model(model: LineSegmentPortableModel) -> None:
    segment_model = model.to_line_segment_model()
    segment = segment_model.to_line_segment()
    reconstructed_segment_model = segment.to_model()
    reconstructed_model = LineSegmentPortableModel.from_line_segment_model(reconstructed_segment_model)
    assert model == reconstructed_model


@pytest.mark.parametrize(
    "model",
    [
        LineSegmentPortableModel(
            name="x",
            type="float",
            size="0xa",
            step="0x1.0p-1",
            start="0x0.0p+0",
            ambient_index="0x0",
            ambient_size="0x64",
        ),
        LineSegmentPortableModel(
            type="float",
            size="0xa",
            step="0x1.0p-1",
            start="0x0.0p+0",
            ambient_index="0x0",
            ambient_size="0x64",
        ),
    ],
)
def test_line_segment_model_float_to_model_from_model(model: LineSegmentPortableModel) -> None:
    segment = model.to_line_segment_model()
    reconstructed_model = LineSegmentPortableModel.from_line_segment_model(segment)
    assert model.name == reconstructed_model.name
    assert model.type == reconstructed_model.type
    assert model.size == reconstructed_model.size
    assert model.ambient_index == reconstructed_model.ambient_index
    assert model.ambient_size == reconstructed_model.ambient_size
    assert isinstance(model.start, str)
    assert isinstance(model.step, str)
    assert isinstance(reconstructed_model.start, str)
    assert isinstance(reconstructed_model.step, str)
    assert hex2float(model.start) == hex2float(reconstructed_model.start)
    assert hex2float(model.step) == hex2float(reconstructed_model.step)
