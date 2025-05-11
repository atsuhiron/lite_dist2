import pytest

from lite_dist2.curriculum_models.study import TrialTableModel
from lite_dist2.curriculum_models.trial import Mapping, Trial, TrialModel, TrialStatus
from lite_dist2.curriculum_models.trial_table import TrialTable
from lite_dist2.expections import LD2ParameterError
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace, ParameterAlignedSpaceModel
from lite_dist2.value_models.base_space import FlattenSegment
from lite_dist2.value_models.jagged_space import ParameterJaggedSpace
from lite_dist2.value_models.line_segment import DummyLineSegment, LineSegmentModel, ParameterRangeInt
from lite_dist2.value_models.point import ScalerValue
from tests.const import DT


@pytest.mark.parametrize(
    ("table", "total_num", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[],  # ここでは使わないので空
                aggregated_parameter_space=None,
                timeout_minutes=1,
            ),
            100,
            FlattenSegment(0, None),
            id="Empty (None aps)",
        ),
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space={-1: [], 0: []},
                timeout_minutes=1,
            ),
            100,
            FlattenSegment(0, None),
            id="Empty",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            10,
            FlattenSegment(10, 0),
            id="Universal 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            None,
            FlattenSegment(10, None),
            id="Infinite 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            10,
            FlattenSegment(10, 40),
            id="Segmented 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            None,
            FlattenSegment(10, 40),
            id="Infinite segmented 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            100,
            FlattenSegment(100, 0),
            id="Universal 2D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            100,
            FlattenSegment(5, 5),
            id="Segmented 2D",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[
                                (1, 0),
                                (1, 1),
                                (1, 2),
                                (1, 3),
                                (1, 4),
                                (1, 5),
                                (1, 6),
                                (1, 7),
                                (1, 8),
                                (1, 9),
                            ],
                            ambient_indices=[
                                (1, 0),
                                (1, 1),
                                (1, 2),
                                (1, 3),
                                (1, 4),
                                (1, 5),
                                (1, 6),
                                (1, 7),
                                (1, 8),
                                (1, 9),
                            ],
                            axes_info=[
                                DummyLineSegment(name="x", type="int", ambient_size=10, step=1),
                                DummyLineSegment(name="y", type="int", ambient_size=10, step=1),
                            ],
                        ),
                        trial_status=TrialStatus.done,
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xa", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xb", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x2", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xc", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x3", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xd", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x4", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xe", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x5", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xf", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x6", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x10", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x7", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x11", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x8", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x12", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x9", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x13", name="p"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[
                                (0, 0),
                                (0, 1),
                                (0, 2),
                                (0, 3),
                                (0, 4),
                            ],
                            ambient_indices=[
                                (0, 0),
                                (0, 1),
                                (0, 2),
                                (0, 3),
                                (0, 4),
                            ],
                            axes_info=[
                                DummyLineSegment(name="x", type="int", ambient_size=10, step=1),
                                DummyLineSegment(name="y", type="int", ambient_size=10, step=1),
                            ],
                        ),
                        trial_status=TrialStatus.done,
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x0", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x1", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x2", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x2", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x3", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x3", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x4", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x4", name="p"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[
                                (0, 5),
                                (0, 6),
                                (0, 7),
                                (0, 8),
                                (0, 9),
                            ],
                            ambient_indices=[
                                (0, 5),
                                (0, 6),
                                (0, 7),
                                (0, 8),
                                (0, 9),
                            ],
                            axes_info=[
                                DummyLineSegment(name="x", type="int", ambient_size=10, step=1),
                                DummyLineSegment(name="y", type="int", ambient_size=10, step=1),
                            ],
                        ),
                        trial_status=TrialStatus.running,
                        result_type="scaler",
                        result_value_type="int",
                    ),
                ],
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
                timeout_minutes=1,
            ),
            100,
            FlattenSegment(20, None),
            id="Infinite jagged running 2D",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    step=1,
                                    size=1,
                                    start=1,
                                    ambient_index=1,
                                    ambient_size=10,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    step=1,
                                    size=10,
                                    start=0,
                                    ambient_index=0,
                                    ambient_size=10,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        trial_status=TrialStatus.done,
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xa", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xb", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x2", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xc", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x3", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xd", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x4", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xe", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x5", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0xf", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x6", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x10", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x7", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x11", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x8", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x12", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x9", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x13", name="p"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    step=1,
                                    size=1,
                                    start=0,
                                    ambient_index=0,
                                    ambient_size=10,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    step=1,
                                    size=5,
                                    start=0,
                                    ambient_index=0,
                                    ambient_size=10,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        trial_status=TrialStatus.done,
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x0", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x1", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x2", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x2", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x3", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x3", name="p"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x4", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x4", name="p"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    step=1,
                                    size=1,
                                    start=0,
                                    ambient_index=0,
                                    ambient_size=10,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    step=1,
                                    size=5,
                                    start=5,
                                    ambient_index=5,
                                    ambient_size=10,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        trial_status=TrialStatus.running,
                        result_type="scaler",
                        result_value_type="int",
                    ),
                ],
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
                timeout_minutes=1,
            ),
            100,
            FlattenSegment(20, None),
            id="Infinite aligned running 2D",
        ),
    ],
)
def test_trial_table_find_least_division(
    table: TrialTable,
    total_num: int,
    expected: FlattenSegment,
) -> None:
    actual = table.find_least_division(total_num)
    assert actual == expected


@pytest.mark.parametrize(
    ("table", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[],  # ここでは使わないので空
                aggregated_parameter_space=None,
                timeout_minutes=1,
            ),
            0,
            id="Empty_aps=None",
        ),
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space={-1: [], 0: []},
                timeout_minutes=1,
            ),
            0,
            id="Empty",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            10,
            id="Universal 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            10,
            id="Infinite 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            20,
            id="Segmented 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            20,
            id="Infinite segmented 1D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            100,
            id="Universal 2D",
        ),
        pytest.param(
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
                timeout_minutes=1,
            ),
            15,
            id="Segmented 2D",
        ),
    ],
)
def test_trial_table_count_grid(
    table: TrialTable,
    expected: int,
) -> None:
    actual = table.count_grid()
    assert actual == expected


@pytest.mark.parametrize(
    "model",
    [
        TrialTableModel(
            trials=[],
            aggregated_parameter_space=None,
            timeout_minutes=1,
        ),
        TrialTableModel(
            trials=[
                TrialModel(
                    study_id="some_study",
                    trial_id="01",
                    timestamp=DT,
                    trial_status=TrialStatus.running,
                    parameter_space=ParameterAlignedSpaceModel(
                        type="aligned",
                        axes=[
                            LineSegmentModel(
                                type="int",
                                size="0xa",
                                step=1,
                                start="0x0",
                                ambient_index="0x0",
                                ambient_size="0x64",
                            ),
                        ],
                        check_lower_filling=True,
                    ),
                    result_type="scaler",
                    result_value_type="float",
                ),
            ],
            aggregated_parameter_space=None,
            timeout_minutes=1,
        ),
        TrialTableModel(
            trials=[
                TrialModel(
                    study_id="some_study",
                    trial_id="01",
                    timestamp=DT,
                    trial_status=TrialStatus.running,
                    parameter_space=ParameterAlignedSpaceModel(
                        type="aligned",
                        axes=[
                            LineSegmentModel(
                                type="int",
                                size="0xa",
                                step=1,
                                start="0x0",
                                ambient_index="0x0",
                                ambient_size="0x64",
                            ),
                        ],
                        check_lower_filling=True,
                    ),
                    result_type="scaler",
                    result_value_type="float",
                    result=[
                        Mapping(
                            param=(
                                ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x1",
                                    name="p1",
                                ),
                            ),
                            result=ScalerValue(
                                type="scaler",
                                value_type="float",
                                value="0x1.0000000000000p+1",
                                name="p2",
                            ),
                        ),
                    ],
                ),
            ],
            aggregated_parameter_space=None,
            timeout_minutes=1,
        ),
    ],
)
def test_trial_table_to_model_from_model(model: TrialTableModel) -> None:
    table = TrialTable.from_model(model)
    reconstructed_model = table.to_model()
    assert model == reconstructed_model


@pytest.mark.parametrize(
    ("trial_table", "trial_id", "result", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x0",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        trial_status=TrialStatus.running,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=100,
                                    start=1,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=None,
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x2",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x2",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                ],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
                timeout_minutes=1,
            ),
            "t02",
            None,
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x0",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        trial_status=TrialStatus.running,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=100,
                                    start=1,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=None,
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x2",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x2",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                ],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
                timeout_minutes=1,
            ),
            id="Do nothing: None result",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x0",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        trial_status=TrialStatus.running,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=100,
                                    start=1,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=None,
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x2",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x2",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                ],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
                timeout_minutes=1,
            ),
            "t02",
            [
                Mapping(
                    param=(
                        ScalerValue(
                            type="scaler",
                            value_type="int",
                            value="0x0",
                            name="x",
                        ),
                        ScalerValue(
                            type="scaler",
                            value_type="int",
                            value="0x1",
                            name="y",
                        ),
                    ),
                    result=ScalerValue(
                        type="scaler",
                        value_type="int",
                        value="0x1",
                        name="p2",
                    ),
                ),
            ],
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x0",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=100,
                                    start=1,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x1",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x1",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x2",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x2",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                ],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=100,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=100,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=100,
                                    start=1,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
                timeout_minutes=1,
            ),
            id="aligned normal",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[(0, 0)],
                            ambient_indices=[(0, 0)],
                            axes_info=[
                                DummyLineSegment(type="int", name="x", ambient_size=6, step=1),
                                DummyLineSegment(type="int", name="y", ambient_size=6, step=1),
                            ],
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x0",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        trial_status=TrialStatus.running,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[(0, 1)],
                            ambient_indices=[(0, 1)],
                            axes_info=[
                                DummyLineSegment(type="int", name="x", ambient_size=6, step=1),
                                DummyLineSegment(type="int", name="y", ambient_size=6, step=1),
                            ],
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=None,
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[(0, 2)],
                            ambient_indices=[(0, 2)],
                            axes_info=[
                                DummyLineSegment(type="int", name="x", ambient_size=6, step=1),
                                DummyLineSegment(type="int", name="y", ambient_size=6, step=1),
                            ],
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x2",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x2",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                ],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=6,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
                timeout_minutes=1,
            ),
            "t02",
            [
                Mapping(
                    param=(
                        ScalerValue(
                            type="scaler",
                            value_type="int",
                            value="0x0",
                            name="x",
                        ),
                        ScalerValue(
                            type="scaler",
                            value_type="int",
                            value="0x1",
                            name="y",
                        ),
                    ),
                    result=ScalerValue(
                        type="scaler",
                        value_type="int",
                        value="0x1",
                        name="p2",
                    ),
                ),
            ],
            TrialTable(
                trials=[
                    Trial(
                        study_id="s01",
                        trial_id="t01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[(0, 0)],
                            ambient_indices=[(0, 0)],
                            axes_info=[
                                DummyLineSegment(type="int", name="x", ambient_size=6, step=1),
                                DummyLineSegment(type="int", name="y", ambient_size=6, step=1),
                            ],
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x0",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t02",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[(0, 1)],
                            ambient_indices=[(0, 1)],
                            axes_info=[
                                DummyLineSegment(type="int", name="x", ambient_size=6, step=1),
                                DummyLineSegment(type="int", name="y", ambient_size=6, step=1),
                            ],
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x1",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x1",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="s01",
                        trial_id="t03",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterJaggedSpace(
                            parameters=[(0, 2)],
                            ambient_indices=[(0, 2)],
                            axes_info=[
                                DummyLineSegment(type="int", name="x", ambient_size=6, step=1),
                                DummyLineSegment(type="int", name="y", ambient_size=6, step=1),
                            ],
                        ),
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x0",
                                        name="x",
                                    ),
                                    ScalerValue(
                                        type="scaler",
                                        value_type="int",
                                        value="0x2",
                                        name="y",
                                    ),
                                ),
                                result=ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x2",
                                    name="p2",
                                ),
                            ),
                        ],
                    ),
                ],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                    1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=2,
                                    ambient_size=6,
                                    start=2,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=0,
                                    ambient_size=6,
                                    start=0,
                                    name="x",
                                ),
                                ParameterRangeInt(
                                    type="int",
                                    size=1,
                                    ambient_index=1,
                                    ambient_size=6,
                                    start=1,
                                    name="y",
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
                timeout_minutes=1,
            ),
            id="jagged normal",
        ),
    ],
)
def test_trial_table_receipt_trial(
    trial_table: TrialTable,
    trial_id: str,
    result: list[Mapping] | None,
    expected: TrialTable,
) -> None:
    trial_table.receipt_trial(trial_id, result)
    actual_model = trial_table.to_model()
    expected_model = expected.to_model()
    assert actual_model.trials == expected_model.trials
    assert actual_model.aggregated_parameter_space == expected_model.aggregated_parameter_space


# noinspection SpellCheckingInspection
def test_trial_table_receipt_trial_raise_override_done_trial() -> None:
    trial_table = TrialTable(
        trials=[
            Trial(
                study_id="s01",
                trial_id="t01",
                timestamp=DT,
                trial_status=TrialStatus.done,
                parameter_space=ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=100, start=0, name="x"),
                        ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=100, start=0, name="y"),
                    ],
                    check_lower_filling=True,
                ),
                result_type="scaler",
                result_value_type="int",
                result=[
                    Mapping(
                        param=(
                            ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                            ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                        ),
                        result=ScalerValue(type="scaler", value_type="int", value="0x0", name="p2"),
                    ),
                ],
            ),
        ],
        aggregated_parameter_space={
            -1: [],
            0: [],
            1: [
                ParameterAlignedSpace(
                    axes=[
                        ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=100, start=0, name="x"),
                        ParameterRangeInt(type="int", size=1, ambient_index=0, ambient_size=100, start=0, name="y"),
                    ],
                    check_lower_filling=True,
                ),
            ],
        },
        timeout_minutes=1,
    )

    result = [
        Mapping(
            param=(
                ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
            ),
            result=ScalerValue(type="scaler", value_type="int", value="0x0", name="p2"),
        ),
    ]

    with pytest.raises(LD2ParameterError, match=r"Cannot\soverride\sresult\sof\sdone\strial"):
        trial_table.receipt_trial("t01", result)


# noinspection SpellCheckingInspection
def test_trial_table_receipt_trial_raise_not_found_trial() -> None:
    trial_table = TrialTable(
        trials=[],
        aggregated_parameter_space={
            -1: [],
            0: [],
            1: [],
        },
        timeout_minutes=1,
    )

    result = [
        Mapping(
            param=(
                ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
            ),
            result=ScalerValue(type="scaler", value_type="int", value="0x0", name="p2"),
        ),
    ]

    with pytest.raises(LD2ParameterError, match=r"Not\sfound\strial\sthat\sid"):
        trial_table.receipt_trial("t01", result)
