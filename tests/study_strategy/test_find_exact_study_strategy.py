import pytest

from lite_dist2.study_strategies.base_study_strategy import StudyStrategyParam
from lite_dist2.study_strategies.find_exact_study_strategy import FindExactStudyStrategy
from lite_dist2.trial import Mapping, Trial, TrialStatus
from lite_dist2.trial_table import TrialTable
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.point import ResultType, ScalerValue
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
}


@pytest.mark.parametrize(
    ("trial_table", "target_value", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            False,
            id="Empty: False",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            False,
            id="Not found: False",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
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
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            True,
            id="Found: True",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.running,
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
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            False,
            id="Found but running: False",
        ),
    ],
)
def test_find_exact_study_strategy_is_done(
    trial_table: TrialTable,
    target_value: ResultType,
    expected: bool,
) -> None:
    strategy = FindExactStudyStrategy(StudyStrategyParam(target_value=target_value))
    actual = strategy.is_done(trial_table, _DUMMY_PARAMETER_SPACE)
    assert actual == expected


@pytest.mark.parametrize(
    ("trial_table", "target_value", "expected"),
    [
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            [],
            id="Empty",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        result=[
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                            Mapping(
                                param=(
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            [],
            id="Not found",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
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
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            [
                Mapping(
                    param=(
                        ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                        ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                    ),
                    result=ScalerValue(type="scaler", value_type="int", value="0x64"),
                ),
            ],
            id="Found",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.running,
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
                                    ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                ),
                                result=ScalerValue(type="scaler", value_type="int", value="0x65"),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
                timeout_minutes=1,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x64"),
            [],
            id="Found but running",
        ),
    ],
)
def test_find_exact_study_strategy_extract_mapping(
    trial_table: TrialTable,
    target_value: ResultType,
    expected: list[Mapping],
) -> None:
    strategy = FindExactStudyStrategy(StudyStrategyParam(target_value=target_value))
    actual = strategy.extract_mappings(trial_table)
    assert actual == expected
