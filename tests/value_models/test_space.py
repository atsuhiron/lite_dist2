import pytest

from lite_dist2.expections import LD2InvalidSpaceError, LD2ParameterError
from lite_dist2.value_models.line_segment import LineSegment, LineSegmentModel, ParameterRangeBool, ParameterRangeInt
from lite_dist2.value_models.space import ParameterAlignedSpace, ParameterAlignedSpaceModel


@pytest.mark.parametrize(
    ("axes", "message"),
    [
        (
            [
                ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
                ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
            ],
            "Invalid space: Filling from lower dimension",
        ),
        (
            [
                ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
                ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
            ],
            "Invalid space: Upper dimension must be size=1",
        ),
        (
            [
                ParameterRangeInt(name="z", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
                ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
                ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
            ],
            "Invalid space: Upper dimension must be size=1",
        ),
        (
            [
                ParameterRangeInt(name="z", type="int", size=1, ambient_index=0, ambient_size=200, start=0),
                ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
                ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=200, start=0),
            ],
            "Invalid space: Upper dimension must be size=1",
        ),
    ],
)
def test_parameter_space_fill_from_lower_raise(
    axes: list[LineSegment],
    message: str,
) -> None:
    with pytest.raises(LD2InvalidSpaceError, match=message):
        _ = ParameterAlignedSpace(axes, check_lower_filling=True)


@pytest.mark.parametrize(
    "axes",
    [
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=2, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=2, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=2, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="z", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="z", type="int", size=2, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="z", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
        [
            ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=2, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="z", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
    ],
)
def test_parameter_space_fill_from_lower_not_raise(axes: list[LineSegment]) -> None:
    space = ParameterAlignedSpace(axes=axes, check_lower_filling=True)
    assert space is not None


@pytest.mark.parametrize(
    ("space", "start_and_sizes", "expected"),
    [
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeBool(type="bool", size=2, ambient_index=0, ambient_size=2, start=False),
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
                ],
                check_lower_filling=False,
            ),
            [(0, 1), (10, 10), (0, 100)],
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeBool(type="bool", size=1, ambient_index=0, ambient_size=2, start=False),
                    ParameterRangeInt(name="x", type="int", size=10, ambient_index=10, ambient_size=100, start=10),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
                ],
                check_lower_filling=False,
            ),
        ),
    ],
)
def test_parameter_aligned_space_slice(
    space: ParameterAlignedSpace,
    start_and_sizes: list[tuple[int, int]],
    expected: ParameterAlignedSpace,
) -> None:
    actual = space.slice(start_and_sizes)
    assert actual == expected


def test_parameter_aligned_space_slice_raise_inconsistent_start_and_sizes() -> None:
    space = ParameterAlignedSpace(
        axes=[
            ParameterRangeBool(type="bool", size=2, ambient_index=0, ambient_size=2, start=False),
            ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
            ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, ambient_size=100, start=0),
        ],
        check_lower_filling=False,
    )
    ss = [(0, 1)]

    with pytest.raises(LD2ParameterError):
        _ = space.slice(ss)


@pytest.mark.parametrize(
    ("one", "other", "target_dim", "expected"),
    [
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=102, start=101),
                ],
                check_lower_filling=False,
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
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0, ambient_size=100),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start=100),
                ],
                check_lower_filling=False,
            ),
            0,
            False,  # not same filling dim False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0, ambient_size=100),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=0, start=0, ambient_size=100),
                ],
                check_lower_filling=False,
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
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(name="x", type="int", size=100, ambient_index=0, start=0),
                    ParameterRangeInt(name="y", type="int", size=100, ambient_index=100, start=100),
                ],
                check_lower_filling=False,
            ),
            0,
            False,  # try merge shallower dim than not filled dim
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100),
                ],
                check_lower_filling=False,
            ),
            0,
            True,  # adjacency True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                check_lower_filling=False,
            ),
            0,
            True,  # adjacency reverse True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101),
                ],
                check_lower_filling=False,
            ),
            0,
            False,  # has stride False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                ],
                check_lower_filling=False,
            ),
            0,
            False,  # has stride reverse False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            0,
            True,  # filled y True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            0,
            True,  # filled y reverse True
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            0,
            False,  # filled y but stride x False
        ),
        (
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=101, start=101, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, name="x"),
                    ParameterRangeInt(type="int", size=1000, ambient_index=0, start=0, name="y", ambient_size=1000),
                ],
                check_lower_filling=False,
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
