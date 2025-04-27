import pytest

from lite_dist2.study import TrialTableModel
from lite_dist2.trial import Mapping, TrialModel, TrialStatus
from lite_dist2.trial_table import TrialTable
from lite_dist2.value_models.line_segment import LineSegmentModel, ParameterRangeInt
from lite_dist2.value_models.point import ScalerValue
from lite_dist2.value_models.space import FlattenSegment, ParameterAlignedSpace, ParameterAlignedSpaceModel
from tests.const import DT


@pytest.mark.parametrize(
    ("table", "total_num", "expected"),
    [
        pytest.param(  # Empty
            TrialTable(
                trials=[],  # ここでは使わないので空
                aggregated_parameter_space=None,
            ),
            100,
            FlattenSegment(0, None),
            id="Empty",
        ),
        pytest.param(  # Empty
            TrialTable(
                trials=[],
                aggregated_parameter_space={-1: [], 0: []},
            ),
            100,
            FlattenSegment(0, None),
            id="Empty",
        ),
        pytest.param(  # Universal 1D
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
            FlattenSegment(10, 0),
            id="Universal 1D",
        ),
        pytest.param(  # Infinite 1D
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
            FlattenSegment(10, None),
            id="Infinite 1D",
        ),
        pytest.param(  # Segmented 1D
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
            FlattenSegment(10, 40),
            id="Segmented 1D",
        ),
        pytest.param(  # Infinite segmented 1D
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
            FlattenSegment(10, 40),
            id="Infinite segmented 1D",
        ),
        pytest.param(  # Universal 2D
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
            FlattenSegment(100, 0),
            id="Universal 2D",
        ),
        pytest.param(  # Segmented 2D
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
            FlattenSegment(5, 5),
            id="Segmented 2D",
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
        pytest.param(  # Empty
            TrialTable(
                trials=[],  # ここでは使わないので空
                aggregated_parameter_space=None,
            ),
            0,
            id="Empty_aps=None",
        ),
        pytest.param(  # Empty
            TrialTable(
                trials=[],
                aggregated_parameter_space={-1: [], 0: []},
            ),
            0,
            id="Empty",
        ),
        pytest.param(  # Universal 1D
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
            id="Universal 1D",
        ),
        pytest.param(  # Infinite 1D
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
            10,
            id="Infinite 1D",
        ),
        pytest.param(  # Segmented 1D
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
            20,
            id="Segmented 1D",
        ),
        pytest.param(  # Infinite segmented 1D
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
            20,
            id="Infinite segmented 1D",
        ),
        pytest.param(  # Universal 2D
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
            id="Universal 2D",
        ),
        pytest.param(  # Segmented 2D
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
        ),
    ],
)
def test_trial_table_to_model_from_model(model: TrialTableModel) -> None:
    table = TrialTable.from_model(model)
    reconstructed_model = table.to_model()
    assert model == reconstructed_model
