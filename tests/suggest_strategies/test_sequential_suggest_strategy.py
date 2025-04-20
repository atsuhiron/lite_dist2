import pytest

from lite_dist2.expections import LD2ParameterError
from lite_dist2.suggest_strategies.sequential_suggest_strategy import SequentialSuggestStrategy
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.space import ParameterAlignedSpace


@pytest.mark.parametrize(
    ("strategy", "flatten_index", "expected"),
    [
        (
            SequentialSuggestStrategy(
                suggest_parameter={},  # 使わない
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=6, start=0, ambient_size=6, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            0,
            (1, 2, 3, 4, 5, 6),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=6, start=0, ambient_size=6, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            2,
            (3, 4, 5, 6),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=7, start=0, ambient_size=7, ambient_index=0),
                        ParameterRangeInt(type="int", size=3, start=0, ambient_size=3, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            0,
            (1, 2, 3, 6, 9, 12, 15, 18, 21),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=7, start=0, ambient_size=7, ambient_index=0),
                        ParameterRangeInt(type="int", size=3, start=0, ambient_size=3, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            1,
            (2, 3),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=7, start=0, ambient_size=7, ambient_index=0),
                        ParameterRangeInt(type="int", size=3, start=0, ambient_size=3, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            4,
            (5, 6),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            876,
            (877, 878, 879, 880),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            800,
            (801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 820, 830, 840, 850, 860, 870, 880, 890, 900, 1000),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            790,
            (791, 792, 793, 794, 795, 796, 797, 798, 799, 800),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            799,
            (800,),
        ),
    ],
)
def test_sequential_suggest_strategy_generate_available_end_finite(
    strategy: SequentialSuggestStrategy,
    flatten_index: int,
    expected: tuple[int, ...],
) -> None:
    actual = strategy._generate_available_end_finite(flatten_index)
    assert actual == expected


@pytest.mark.parametrize(
    ("strategy", "flatten_index", "expected"),
    [
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            0,
            ((1,), True),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            4,
            ((5,), True),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            4,
            ((5, 6, 7, 8, 9, 10), False),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            9,
            ((10,), False),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            10,
            ((11, 12, 13, 14, 15, 16, 17, 18, 19, 20), True),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            10,
            ((11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 30, 40, 50, 60, 70, 80, 90, 100), False),
        ),
        (
            SequentialSuggestStrategy(
                suggest_parameter={},
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=None, start=0, ambient_size=None, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                        ParameterRangeInt(type="int", size=10, start=0, ambient_size=10, ambient_index=0),
                    ],
                    check_lower_filling=True,
                ),
            ),
            100,
            ((101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200), True),
        ),
    ],
)
def test_sequential_suggest_strategy_generate_available_end_infinite(
    strategy: SequentialSuggestStrategy,
    flatten_index: int,
    expected: tuple[tuple[int, ...], bool],
) -> None:
    actual = strategy._generate_available_end_infinite(flatten_index)
    assert actual == expected


@pytest.mark.parametrize(
    ("init", "ratio", "iter_num", "expected"),
    [
        ((1, 2, 3), 3, 5, (1, 2, 3, 6, 9)),
        ((1, 2, 3, 4), 10, 3, (1, 2, 3)),
    ],
)
def test_sequential_suggest_strategy_infinite_available_generator(
    init: tuple[int, ...],
    ratio: int,
    iter_num: int,
    expected: tuple[int, ...],
) -> None:
    generator = SequentialSuggestStrategy._infinite_available_generator(init, ratio)
    actual = []
    for i, v in enumerate(generator):
        if i >= iter_num:
            break
        actual.append(v)
    actual = tuple(actual)
    assert actual == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 1),
        (None, 2, 2),
        (3, None, 3),
    ],
)
def test_sequential_suggest_strategy_nullable_min(a: int | None, b: int | None, expected: int) -> None:
    actual = SequentialSuggestStrategy._nullable_min(a, b)
    assert actual == expected


def test_sequential_suggest_strategy_nullable_min_raise_both_none() -> None:
    with pytest.raises(LD2ParameterError, match=r"both\sis\sNone"):
        _ = SequentialSuggestStrategy._nullable_min(None, None)
