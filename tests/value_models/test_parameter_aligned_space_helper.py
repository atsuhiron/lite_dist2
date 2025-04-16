import pytest

from lite_dist2.value_models.parameter_aligned_space_helper import remap_space, simplify
from lite_dist2.value_models.space import ParameterAlignedSpace, ParameterRangeInt


@pytest.mark.parametrize(
    ("sub_spaces", "target_dim", "expected"),
    [
        (  # empty
            [],
            0,
            [],
        ),
        (  # single
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # far double
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # far double reversed
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # adjacency double
            [
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
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=200, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # adjacency reversed double
            [
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
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=200, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # adjacency triple
            [
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
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=300, ambient_index=0, start=0),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # false adjacency (different dimension)
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=10, ambient_index=0, ambient_size=20, start=0),
                    ],
                    check_lower_filling=True,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=1, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=10, ambient_index=10, ambient_size=20, start=10),
                    ],
                    check_lower_filling=True,
                ),
            ],
            1,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=10, ambient_index=0, ambient_size=20, start=0),
                    ],
                    check_lower_filling=True,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=1, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=10, ambient_index=10, ambient_size=20, start=10),
                    ],
                    check_lower_filling=True,
                ),
            ],
        ),
        (  # true adjacency (same dimension)
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=10, ambient_index=0, ambient_size=20, start=0),
                    ],
                    check_lower_filling=True,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=10, ambient_index=10, ambient_size=20, start=10),
                    ],
                    check_lower_filling=True,
                ),
            ],
            1,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(name="x", type="int", size=1, ambient_index=0, ambient_size=100, start=0),
                        ParameterRangeInt(name="y", type="int", size=20, ambient_index=0, ambient_size=20, start=0),
                    ],
                    check_lower_filling=True,
                ),
            ],
        ),
    ],
)
def test_simplify_table_by_dim(
    sub_spaces: list[ParameterAlignedSpace],
    target_dim: int,
    expected: list[ParameterAlignedSpace],
) -> None:
    actual = simplify(sub_spaces, target_dim)
    assert actual == expected


@pytest.mark.parametrize(
    ("aps", "dim", "expected"),
    [
        (
            [],
            3,
            {-1: [], 0: [], 1: [], 2: []},
        ),
        (
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=10, start=0),
                        ParameterRangeInt(type="int", size=10, ambient_index=0, ambient_size=100, start=0),
                    ],
                    check_lower_filling=True,
                ),
            ],
            2,
            {
                -1: [],
                0: [],
                1: [
                    ParameterAlignedSpace(
                        axes=[
                            ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=10, start=0),
                            ParameterRangeInt(type="int", size=10, ambient_index=0, ambient_size=100, start=0),
                        ],
                        check_lower_filling=True,
                    ),
                ],
            },
        ),
        (
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=10, start=0),
                        ParameterRangeInt(type="int", size=100, ambient_index=0, ambient_size=100, start=0),
                    ],
                    check_lower_filling=True,
                ),
            ],
            2,
            {
                -1: [],
                0: [
                    ParameterAlignedSpace(
                        axes=[
                            ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=10, start=0),
                            ParameterRangeInt(type="int", size=100, ambient_index=0, ambient_size=100, start=0),
                        ],
                        check_lower_filling=True,
                    ),
                ],
                1: [],
            },
        ),
    ],
)
def test_remap_space(
    aps: list[ParameterAlignedSpace],
    dim: int,
    expected: dict[int, list[ParameterAlignedSpace]],
) -> None:
    actual = remap_space(aps, dim)
    assert actual == expected
