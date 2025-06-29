import pytest

from lite_dist2.curriculum_models.mapping import Mapping, MappingsStorage
from lite_dist2.curriculum_models.trial import Trial, TrialStatus
from lite_dist2.curriculum_models.trial_table import TrialTable
from lite_dist2.expections import LD2NotDoneError
from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.point import ScalarValue, VectorValue
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
    "reserved_timestamp": DT,
    "const_param": None,
    "parameter_space": _DUMMY_PARAMETER_SPACE,
    "result_type": "scalar",
    "result_value_type": "int",
    "worker_node_name": "w01",
    "worker_node_id": "w01",
}


@pytest.fixture
def done_grid_fixture(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    return_value = request.param

    # noinspection PyUnusedLocal
    def fake_count_grid(self) -> int:  # noqa: ANN001
        return return_value

    monkeypatch.setattr(TrialTable, "count_grid", fake_count_grid)


@pytest.fixture
def all_grid_fixture(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    return_value = request.param

    # noinspection PyUnusedLocal
    def fake_get_total(self) -> int:  # noqa: ANN001
        return return_value

    monkeypatch.setattr(ParameterAlignedSpace, "get_total", fake_get_total)


@pytest.mark.parametrize(
    ("done_grid_fixture", "all_grid_fixture", "expected"),
    [
        pytest.param(10, 10, True, id="Done"),
        pytest.param(9, 10, False, id="Yet"),
    ],
    indirect=["done_grid_fixture", "all_grid_fixture"],
)
def test_all_calculation_study_strategy_is_done2(
    done_grid_fixture: int,
    all_grid_fixture: int,
    expected: bool,
) -> None:
    strategy = AllCalculationStudyStrategy(study_strategy_param=None)
    trial_table = TrialTable(trials=[], aggregated_parameter_space=None)
    parameter_space = ParameterAlignedSpace(
        axes=[
            ParameterRangeInt(name="x", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
            ParameterRangeInt(name="y", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
        ],
        check_lower_filling=True,
    )
    actual = strategy.is_done(trial_table, parameter_space)
    assert actual == expected


@pytest.mark.parametrize(
    ("trial_table", "expected"),
    [
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
            MappingsStorage(
                params_info=(
                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                ),
                result_info=ScalarValue(type="scalar", value_type="int", value="0x0"),
                values=[
                    ("0x1", "0x1", "0x67"),
                ],
            ),
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
            MappingsStorage(
                params_info=(
                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                ),
                result_info=ScalarValue(type="scalar", value_type="int", value="0x0"),
                values=[
                    ("0x1", "0x1", "0x67"),
                    ("0x2", "0x2", "0x68"),
                    ("0x3", "0x3", "0x69"),
                    ("0x4", "0x4", "0x6a"),
                ],
            ),
            id="Multi trial, multi map, scalar",
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
                                result=VectorValue(type="vector", value_type="int", values=["0x67", "0x67"]),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x2", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x2", name="y"),
                                ),
                                result=VectorValue(type="vector", value_type="int", values=["0x68", "0x68"]),
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
                                result=VectorValue(type="vector", value_type="int", values=["0x69", "0x69"]),
                            ),
                            Mapping(
                                params=(
                                    ScalarValue(type="scalar", value_type="int", value="0x4", name="x"),
                                    ScalarValue(type="scalar", value_type="int", value="0x4", name="y"),
                                ),
                                result=VectorValue(type="vector", value_type="int", values=["0x6a", "0x6a"]),
                            ),
                        ],
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            MappingsStorage(
                params_info=(
                    ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                    ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                ),
                result_info=VectorValue(type="vector", value_type="int", values=["0x0", "0x0"]),
                values=[
                    ("0x1", "0x1", "0x67", "0x67"),
                    ("0x2", "0x2", "0x68", "0x68"),
                    ("0x3", "0x3", "0x69", "0x69"),
                    ("0x4", "0x4", "0x6a", "0x6a"),
                ],
            ),
            id="Multi trial, multi map, vector",
        ),
    ],
)
def test_find_exact_study_strategy_extract_mapping(
    trial_table: TrialTable,
    expected: MappingsStorage,
) -> None:
    strategy = AllCalculationStudyStrategy(None)
    actual = strategy.extract_mappings(trial_table)
    assert actual == expected


@pytest.mark.parametrize(
    "trial_table",
    [
        pytest.param(
            TrialTable(
                trials=[],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            id="Empty",
        ),
        pytest.param(
            TrialTable(
                trials=[
                    Trial(
                        trial_id="t01",
                        trial_status=TrialStatus.done,
                        results=None,
                        **_TRIAL_ARGS,
                    ),
                    Trial(
                        trial_id="t02",
                        trial_status=TrialStatus.done,
                        results=None,
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            id="None first",
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
                        results=None,
                        **_TRIAL_ARGS,
                    ),
                ],
                aggregated_parameter_space=_DUMMY_APS,
            ),
            id="None",
        ),
    ],
)
def test_find_exact_study_strategy_extract_mapping_raise(trial_table: TrialTable) -> None:
    strategy = AllCalculationStudyStrategy(None)
    with pytest.raises(LD2NotDoneError):
        _ = strategy.extract_mappings(trial_table)
