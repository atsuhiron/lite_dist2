import itertools
from typing import Any

import pytest

from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.base_space import FlattenSegment
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.parameter_aligned_space_helper import infinite_product, remap_space, simplify


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
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # far double
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # far double reversed
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # adjacency double
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=200, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # adjacency reversed double
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=200, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
        ),
        (  # adjacency triple
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=100, start=100, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=0, start=0, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=100, ambient_index=200, start=200, ambient_size=None),
                    ],
                    check_lower_filling=False,
                ),
            ],
            0,
            [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=300, ambient_index=0, start=0, ambient_size=None),
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
def test_simplify(
    sub_spaces: list[ParameterAlignedSpace],
    target_dim: int,
    expected: list[ParameterAlignedSpace],
) -> None:
    actual = simplify(sub_spaces, target_dim)
    assert actual == expected


@pytest.mark.parametrize(
    ("segments", "expected"),
    [
        pytest.param(
            [
                FlattenSegment(0, 5),
                FlattenSegment(5, 5),
                FlattenSegment(10, 5),
            ],
            [
                FlattenSegment(0, 15),
            ],
            id="continuing 3",
        ),
    ],
)
def test_simplify_simple_flatten(segments: list[FlattenSegment], expected: list[FlattenSegment]) -> None:
    actual = simplify(segments)
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


@pytest.mark.parametrize(
    ("iterators", "max_num", "expected"),
    [
        (
            (range(8),),
            3,
            [(0,), (1,), (2,)],
        ),
        (
            (range(8), range(4)),
            5,
            [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)],
        ),
        (
            (itertools.count(0),),
            3,
            [(0,), (1,), (2,)],
        ),
        (
            (itertools.count(0), range(4)),
            5,
            [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)],
        ),
    ],
)
def test_infinite_product(iterators: tuple[iter, ...], max_num: int, expected: list[tuple[Any, ...]]) -> None:
    actual = []
    for item in infinite_product(*iterators):
        actual.append(item)
        if len(actual) >= max_num:
            break
    assert actual == expected


def test_infinite_product_islice() -> None:
    # noinspection PyTypeChecker
    gen = infinite_product(*(itertools.count(0), (x for x in range(8))))
    gen = itertools.islice(gen, 6, None)
    item = next(gen)
    assert item == (0, 6)
    item = next(gen)
    assert item == (0, 7)
    item = next(gen)
    assert item == (1, 0)
    item = next(gen)
    assert item == (1, 1)


def test_infinite_product_enumerate_islice() -> None:
    # noinspection PyTypeChecker
    gen = infinite_product(*(itertools.count(0), (x for x in range(8))))
    gen = enumerate(itertools.islice(gen, 6, None))
    item = next(gen)
    assert item == (0, (0, 6))
    item = next(gen)
    assert item == (1, (0, 7))
    item = next(gen)
    assert item == (2, (1, 0))
    item = next(gen)
    assert item == (3, (1, 1))
