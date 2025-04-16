import pytest

from lite_dist2.trial_table import DivisionType, TrialTable
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.space import ParameterAlignedSpace


@pytest.mark.parametrize(
    ("table", "total_num", "expected"),
    [
        (  # Empty
            TrialTable(
                trials=[],  # ここでは使わないので空
                aggregated_parameter_space=None,
            ),
            100,
            (DivisionType.half_line, 0),
        ),
        (  # Empty
            TrialTable(
                trials=[],
                aggregated_parameter_space={-1: [], 0: []},
            ),
            100,
            (DivisionType.half_line, 0),
        ),
        (  # Universal 1D
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=10,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                    0: [],
                },
            ),
            10,
            (DivisionType.no_division, 10),
        ),
        (  # Infinite 1D
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [],
                    0: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=None,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
            ),
            None,
            (DivisionType.half_line, 10),
        ),
        (  # Segmented 1D
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [],
                    0: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=10,
                                    ambient_index=50,
                                    ambient_size=100,
                                    start=50,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
            ),
            10,
            (DivisionType.segment, 10),
        ),
        (  # Infinite segmented 1D
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [],
                    0: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=None,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=10,
                                    ambient_index=50,
                                    ambient_size=None,
                                    start=50,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
            ),
            None,
            (DivisionType.segment, 10),
        ),
        (  # Universal 2D
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=10,
                                    start=0,
                                    step=1,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=10,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                    0: [],
                    1: [],
                },
            ),
            100,
            (DivisionType.no_division, 100),
        ),
        (  # Segmented 2D
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [],
                    0: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=10,
                                    start=1,
                                    step=1,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    size=10,
                                    ambient_index=0,
                                    ambient_size=10,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=10,
                                    start=0,
                                    step=1,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    size=5,
                                    ambient_index=0,
                                    ambient_size=10,
                                    start=0,
                                    step=1,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
            ),
            100,
            (DivisionType.segment, 5),
        ),
    ],
)
def test_trial_table_find_least_division(
    table: TrialTable,
    total_num: int,
    expected: tuple[DivisionType, int],
) -> None:
    actual = table.find_least_division(total_num)
    assert actual == expected
