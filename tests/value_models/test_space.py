import pytest

from lite_dist2.value_models.space import ParameterAlignedSpace, ParameterRangeInt


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
