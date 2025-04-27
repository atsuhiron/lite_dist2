import pytest

from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.trial import Mapping, Trial, TrialStatus
from lite_dist2.trial_table import TrialTable
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.point import ScalerValue
from lite_dist2.value_models.space import ParameterAlignedSpace
from tests.const import DT


@pytest.mark.parametrize(
    ("strategy", "trial_table", "parameter_space", "expected"),
    [
        pytest.param(
            AllCalculationStudyStrategy(study_strategy_param=None),
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
            AllCalculationStudyStrategy(study_strategy_param=None),
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
            AllCalculationStudyStrategy(study_strategy_param=None),
            TrialTable(
                trials=[
                    Trial(
                        study_id="01",
                        trial_id="01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x2", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                            ),
                        ],
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
            AllCalculationStudyStrategy(study_strategy_param=None),
            TrialTable(
                trials=[
                    Trial(
                        study_id="01",
                        trial_id="01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x2", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="01",
                        trial_id="02",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x3", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x67"),
                            ),
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x4", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x68"),
                            ),
                            Mapping(
                                param=(ScalerValue(type="scaler", value_type="int", value="0x5", name="x"),),
                                result=ScalerValue(type="scaler", value_type="int", value="0x69"),
                            ),
                        ],
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
            AllCalculationStudyStrategy(study_strategy_param=None),
            TrialTable(
                trials=[
                    Trial(
                        study_id="01",
                        trial_id="01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="01",
                        trial_id="02",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x67"),
                            ),
                        ],
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
            AllCalculationStudyStrategy(study_strategy_param=None),
            TrialTable(
                trials=[
                    Trial(
                        study_id="01",
                        trial_id="01",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x64"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                        ],
                    ),
                    Trial(
                        study_id="01",
                        trial_id="02",
                        timestamp=DT,
                        trial_status=TrialStatus.done,
                        parameter_space=ParameterAlignedSpace(
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
                        result_type="scaler",
                        result_value_type="int",
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x67"),
                            ),
                        ],
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
    strategy: AllCalculationStudyStrategy,
    trial_table: TrialTable,
    parameter_space: ParameterAlignedSpace,
    expected: bool,
) -> None:
    actual = strategy.is_done(trial_table, parameter_space)
    assert actual == expected
