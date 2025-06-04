import pytest

from lite_dist2.curriculum_models.trial import Mapping, Trial, TrialStatus
from lite_dist2.curriculum_models.trial_table import TrialTable
from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.point import ScalarValue
from tests.const import DT

_DUMMY_PARAMETER_SPACE = ParameterAlignedSpace(
    axes=[
        ParameterRangeInt(name="x", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
        ParameterRangeInt(name="y", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
    ],
    check_lower_filling=True,
)
_DUMMY_APS = {-1: [], 0: [], 1: []}
_TRIAL_ARGS = {
    "study_id": "s01",
    "timestamp": DT,
    "parameter_space": _DUMMY_PARAMETER_SPACE,
    "result_type": "scalar",
    "result_value_type": "int",
    "worker_node_name": "w01",
}


@pytest.mark.parametrize(
    ("trial_table", "parameter_space", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space=None,
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(
                        name="x",
                        type="int",
                        size=6,
                        start=0,
                        ambient_size=6,
                        ambient_index=0,
                    ),
                ],
                check_lower_filling=True,
            ),
            False,
            id="init not defined",
        ),
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space={
                    -1: [],
                    0: [],
                },
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(
                        name="x",
                        type="int",
                        size=6,
                        start=0,
                        ambient_size=6,
                        ambient_index=0,
                    ),
                ],
                check_lower_filling=True,
            ),
            False,
            id="init",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x65"),
                            ),
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x66"),
                            ),
                        ],
                        **_TRIAL_ARGS,
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
                                    size=3,
                                    start=0,
                                    ambient_size=6,
                                    ambient_index=0,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(
                        name="x",
                        type="int",
                        size=6,
                        start=0,
                        ambient_size=6,
                        ambient_index=0,
                    ),
                ],
                check_lower_filling=True,
            ),
            False,
            id="continuing",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x65"),
                            ),
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x66"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                    Trial(
                        trial_id="t02",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x3", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                            ),
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x4", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x68"),
                            ),
                            Mapping(
                                params=(ScalarValue(type="scalar", value_type="int", value="0x5", name="x"),),
                                result=ScalarValue(type="scalar", value_type="int", value="0x69"),
                            ),
                        ],
                        **_TRIAL_ARGS,
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
                                    size=3,
                                    start=0,
                                    ambient_size=6,
                                    ambient_index=0,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    size=3,
                                    start=3,
                                    ambient_size=6,
                                    ambient_index=3,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                },
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(
                        name="x",
                        type="int",
                        size=6,
                        start=0,
                        ambient_size=6,
                        ambient_index=0,
                    ),
                ],
                check_lower_filling=True,
            ),
            True,
            id="done 1D",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x65"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                    Trial(
                        trial_id="02",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x66"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                            ),
                        ],
                        **_TRIAL_ARGS,
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
                                    start=0,
                                    ambient_size=2,
                                    ambient_index=0,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    size=2,
                                    start=0,
                                    ambient_size=2,
                                    ambient_index=0,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    size=1,
                                    start=1,
                                    ambient_size=2,
                                    ambient_index=1,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    size=2,
                                    start=0,
                                    ambient_size=2,
                                    ambient_index=0,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                    1: [],
                },
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(
                        name="x",
                        type="int",
                        size=2,
                        start=0,
                        ambient_size=2,
                        ambient_index=0,
                    ),
                    ParameterRangeInt(
                        name="y",
                        type="int",
                        size=2,
                        start=0,
                        ambient_size=2,
                        ambient_index=0,
                    ),
                ],
                check_lower_filling=True,
            ),
            True,
            id="done 2D not aggregated",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x65"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                    Trial(
                        trial_id="02",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x66"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space={
                    -1: [
                        ParameterAlignedSpace(
                            axes=[
                                ParameterRangeInt(
                                    name="x",
                                    type="int",
                                    size=2,
                                    start=0,
                                    ambient_size=2,
                                    ambient_index=0,
                                ),
                                ParameterRangeInt(
                                    name="y",
                                    type="int",
                                    size=2,
                                    start=0,
                                    ambient_size=2,
                                    ambient_index=0,
                                ),
                            ],
                            check_lower_filling=True,
                        ),
                    ],
                    0: [],
                    1: [],
                },
            ),
            ParameterAlignedSpace(
                axes=[
                    ParameterRangeInt(
                        name="x",
                        type="int",
                        size=2,
                        start=0,
                        ambient_size=2,
                        ambient_index=0,
                    ),
                    ParameterRangeInt(
                        name="y",
                        type="int",
                        size=2,
                        start=0,
                        ambient_size=2,
                        ambient_index=0,
                    ),
                ],
                check_lower_filling=True,
            ),
            True,
            id="done 2D aggregated",
        ),
    ],
)
def test_all_calculation_study_strategy_is_done(
    trial_table: TrialTable,
    parameter_space: ParameterAlignedSpace,
    expected: bool,
) -> None:
    strategy = AllCalculationStudyStrategy(study_strategy_param=None)
    actual = strategy.is_done(trial_table, parameter_space)
    assert actual == expected


@pytest.mark.parametrize(
    ("trial_table", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            [],
            id="Empty",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            [
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                ),
            ],
            id="Single trial, single map",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x2", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x68"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                    Trial(
                        trial_id="t02",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x3", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x3", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x69"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x4", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x4", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x6a"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            [
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                ),
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x2", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x68"),
                ),
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x3", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x3", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x69"),
                ),
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x4", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x4", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x6a"),
                ),
            ],
            id="Multi trial, multi map",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x2", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x68"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                    Trial(
                        trial_id="t02",
                        trial_status=TrialStatus.running,
                        results=[
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x3", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x3", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x69"),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x4", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x4", name="y"),
                                ),
                                result=ScalarValue(type="scalar", value_type="int", value="0x6a"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            [
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x1", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x67"),
                ),
                Mapping(
                    params=(
                        ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),
                        ScalarValue(type="scalar", value_type="int", value="0x2", name="y"),
                    ),
                    result=ScalarValue(type="scalar", value_type="int", value="0x68"),
                ),
            ],
            id="Multi trial, multi map, except running",
        ),
    ],
)
def test_find_exact_study_strategy_extract_mapping(
    trial_table: TrialTable,
    expected: list[Mapping],
) -> None:
    strategy = AllCalculationStudyStrategy(None)
    actual = strategy.extract_mappings(trial_table)
    assert actual == expected
