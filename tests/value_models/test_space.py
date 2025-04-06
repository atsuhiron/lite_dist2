import pytest

from lite_dist2.value_models.line_segment import (
    LineSegment,
    ParameterRangeBool,
    ParameterRangeFloat,
    ParameterRangeInt,
)
from lite_dist2.value_models.space import ParameterAlignedSpace


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
    ("one", "other", "target_dim", "expected"),
    [
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False, False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=102, start=101),
                ],
                filling_dim=[False],
            ),
            0,
            False,  # not derived by same ambient space False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False, False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start=100),
                ],
                filling_dim=[True, False],
            ),
            0,
            False,  # not same filling dim False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start=100),
                ],
                filling_dim=[True, True],
            ),
            1,
            False,  # try merge filling dim
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False, False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start=100),
                ],
                filling_dim=[False, False],
            ),
            0,
            False,  # try merge shallower dim than not filled dim
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100),
                ],
                filling_dim=[False],
            ),
            0,
            True,  # adjacency True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False],
            ),
            0,
            True,  # adjacency reverse True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101),
                ],
                filling_dim=[False],
            ),
            0,
            False,  # has stride False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                filling_dim=[False],
            ),
            0,
            False,  # has stride reverse False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            True,  # filled y True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            True,  # filled y reverse True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            False,  # filled y but stride x False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            False,  # filled y but stride x reverse False
        ),
    ],
)
def test_parameter_aligned_space_can_merge(
    one: ParameterAlignedSpace,
    other: ParameterAlignedSpace,
    target_dim: int,
    expected: bool,
) -> None:
    actual = one.can_merge(other, target_dim)
    actual_reversed = other.can_merge(one, target_dim)
    assert actual == expected
    assert actual_reversed == expected
