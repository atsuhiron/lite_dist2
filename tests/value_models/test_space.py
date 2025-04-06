import pytest

from lite_dist2.value_models.space import (
    LineSegment,
    ParameterAlignedSpace,
    ParameterRangeBool,
    ParameterRangeFloat,
    ParameterRangeInt,
)


@pytest.mark.parametrize(
    ("one", "other", "expected"),
    [
        (  # complete match True
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            True,
        ),
        (  # different start True
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=16, ambient_size="ff", start="10", step=1),
            True,
        ),
        (  # different size True
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=16, ambient_size="ff", start="10", step=1),
            True,
        ),
        (  # different name False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeInt(name="y", type="int", size=100, ambient_index=16, ambient_size="ff", start="10", step=1),
            False,
        ),
        (  # different type False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size="2", start=True, step=1),
            False,
        ),
        (  # different ambient_size False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=16, ambient_size="f0", start="10", step=1),
            False,
        ),
        (  # different step False
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size="ff", start="0", step=1),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=16, ambient_size="ff", start="10", step=2),
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
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size="2", start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size="2", start=False),
            True,
        ),
        (  # adjacency True
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=0, ambient_size="2", start=False),
            ParameterRangeBool(name="x", type="bool", size=1, ambient_index=1, ambient_size="2", start=True),
            True,
        ),
        (  # complete match True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size="ff", start="0"),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size="ff", start="0"),
            True,
        ),
        (  # adjacency True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size="ff", start="0"),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=10, ambient_size="ff", start="a"),
            True,
        ),
        (  # overlap True
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size="ff", start="0"),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=5, ambient_size="ff", start="5"),
            True,
        ),
        (  # stride False
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=0, ambient_size="ff", start="0"),
            ParameterRangeInt(name="x", type="int", size=10, ambient_index=11, ambient_size="ff", start="b"),
            False,
        ),
        (  # Complete match True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size="ff", start="0x0.0p+0", step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size="ff", start="0x0.0p+0", step=1),
            True,
        ),
        (  # overlap True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size="ff", start="0x0.0p+0", step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=5, ambient_size="ff", start="0x5.0p+0", step=1),
            True,
        ),
        (  # adjacency True
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size="ff", start="0x0.0p+0", step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=10, ambient_size="ff", start="0xa.0p+0", step=1),
            True,
        ),
        (  # stride False
            ParameterRangeFloat(type="float", size=10, ambient_index=0, ambient_size="ff", start="0x0.0p+0", step=1),
            ParameterRangeFloat(type="float", size=10, ambient_index=11, ambient_size="ff", start="0xb.0p+0", step=1),
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
    ("seg", "expected"),
    [
        (ParameterRangeBool(type="bool", size=1, ambient_index=0, ambient_size="2", start=False), 0),
        (ParameterRangeBool(type="bool", size=1, ambient_index=1, ambient_size="1", start=True), 1),
        (ParameterRangeInt(type="int", size=10, ambient_index=0, ambient_size="ffff", start="0"), 9),
        (ParameterRangeInt(type="int", size=10, ambient_index=5, ambient_size="ffff", start="0"), 14),
        (ParameterRangeFloat(type="float", size=5, ambient_index=0, ambient_size="ff", start="0xb.0p+0", step=1), 4),
        (ParameterRangeFloat(type="float", size=5, ambient_index=2, ambient_size="ff", start="0xb.0p+0", step=1), 6),
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
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False, False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=102, start="65"),
                ],
                filling_dim=[False],
            ),
            0,
            False,  # not derived by same ambient space False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False, False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start="64"),
                ],
                filling_dim=[True, False],
            ),
            0,
            False,  # not same filling dim False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start="64"),
                ],
                filling_dim=[True, True],
            ),
            1,
            False,  # try merge filling dim
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False, False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start="0"),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start="64"),
                ],
                filling_dim=[False, False],
            ),
            0,
            False,  # try merge shallower dim than not filled dim
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start="64"),
                ],
                filling_dim=[False],
            ),
            0,
            True,  # adjacency True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start="64"),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False],
            ),
            0,
            True,  # adjacency reverse True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start="65"),
                ],
                filling_dim=[False],
            ),
            0,
            False,  # has stride False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start="65"),
                ],
                filling_dim=[False],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0"),
                ],
                filling_dim=[False],
            ),
            0,
            False,  # has stride reverse False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start="64", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            True,  # filled y True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start="64", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            True,  # filled y reverse True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start="65", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            0,
            False,  # filled y but stride x False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start="65", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
                ],
                filling_dim=[False, True],
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start="0", name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start="0", name="y"),
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
