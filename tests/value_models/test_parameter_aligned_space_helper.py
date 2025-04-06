import pytest

from lite_dist2.value_models.parameter_aligned_space_helper import simplify_table_by_dim
from lite_dist2.value_models.space import ParameterAlignedSpace, ParameterRangeInt


@pytest.mark.parametrize(
    ("sub_spaces", "expected"),
    [
        (  # empty
            [],
            [],
        ),
        (  # single
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
            ],
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
            ],
        ),
        (  # far double
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    filling_dim=[False],
                ),
            ],
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    filling_dim=[False],
                ),
            ],
        ),
        (  # far double reversed
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    filling_dim=[False],
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
            ],
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    filling_dim=[False],
                ),
            ],
        ),
        (  # adjacency double
            [
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
            ],
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=200, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
            ],
        ),
        (  # adjacency reversed double
            [
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
            ],
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=200, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
            ],
        ),
        (  # adjacency triple
            [
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
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200),
                    ],
                    filling_dim=[False],
                ),
            ],
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=300, ambient_index=0, start=0),
                    ],
                    filling_dim=[False],
                ),
            ],
        ),
    ],
)
def test_simplify_table_by_dim(sub_spaces: list[ParameterAlignedSpace], expected: list[ParameterAlignedSpace]) -> None:
    actual = simplify_table_by_dim(sub_spaces, 0)
    assert actual == expected
