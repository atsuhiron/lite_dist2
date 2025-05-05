import pytest

from lite_dist2.trial import Mapping, Trial, TrialModel, TrialStatus
from lite_dist2.value_models.aligned_space import ParameterAlignedSpaceModel
from lite_dist2.value_models.jagged_space import ParameterJaggedSpace, ParameterJaggedSpaceModel
from lite_dist2.value_models.line_segment import DummyLineSegment, LineSegmentModel
from lite_dist2.value_models.point import ResultType, ScalerValue, VectorValue
from tests.const import DT

_dummy_space = ParameterJaggedSpace(
    parameters=[(0, 1)],
    ambient_indices=[(0, 1)],
    axes_info=[DummyLineSegment(name="x", type="int", ambient_size=6, step=1)],
)


@pytest.mark.parametrize(
    ("trial", "target", "expected"),
    [
        pytest.param(
            Trial(
                study_id="s01",
                trial_id="t01",
                timestamp=DT,
                trial_status=TrialStatus.running,
                parameter_space=_dummy_space,
                result_type="scaler",
                result_value_type="int",
                result=[
                    Mapping(
                        param=(ScalerValue(type="scaler", value_type="int", value="0x0"),),
                        result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                    ),
                    Mapping(
                        param=(ScalerValue(type="scaler", value_type="int", value="0x1"),),
                        result=ScalerValue(type="scaler", value_type="int", value="0x67"),
                    ),
                ],
            ),
            ScalerValue(type="scaler", value_type="int", value="0x66"),
            None,
            id="not found: running",
        ),
        pytest.param(
            Trial(
                study_id="s01",
                trial_id="t01",
                timestamp=DT,
                trial_status=TrialStatus.done,
                parameter_space=_dummy_space,
                result_type="scaler",
                result_value_type="int",
                result=None,
            ),
            ScalerValue(type="scaler", value_type="int", value="0x66"),
            None,
            id="not found: none result",
        ),
        pytest.param(
            Trial(
                study_id="s01",
                trial_id="t01",
                timestamp=DT,
                trial_status=TrialStatus.done,
                parameter_space=_dummy_space,
                result_type="scaler",
                result_value_type="int",
                result=[],
            ),
            ScalerValue(type="scaler", value_type="int", value="0x66"),
            None,
            id="not found: empty result",
        ),
        pytest.param(
            Trial(
                study_id="s01",
                trial_id="t01",
                timestamp=DT,
                trial_status=TrialStatus.done,
                parameter_space=_dummy_space,
                result_type="scaler",
                result_value_type="int",
                result=[
                    Mapping(
                        param=(ScalerValue(type="scaler", value_type="int", value="0x0"),),
                        result=ScalerValue(type="scaler", value_type="int", value="0x66"),
                    ),
                    Mapping(
                        param=(ScalerValue(type="scaler", value_type="int", value="0x1"),),
                        result=ScalerValue(type="scaler", value_type="int", value="0x67"),
                    ),
                ],
            ),
            ScalerValue(type="scaler", value_type="int", value="0x66"),
            Mapping(
                param=(ScalerValue(type="scaler", value_type="int", value="0x0"),),
                result=ScalerValue(type="scaler", value_type="int", value="0x66"),
            ),
            id="found: scaler",
        ),
        pytest.param(
            Trial(
                study_id="s01",
                trial_id="t01",
                timestamp=DT,
                trial_status=TrialStatus.done,
                parameter_space=_dummy_space,
                result_type="vector",
                result_value_type="int",
                result=[
                    Mapping(
                        param=(ScalerValue(type="scaler", value_type="int", value="0x0"),),
                        result=VectorValue(type="vector", value_type="int", values=["0x66", "0x2328"]),
                    ),
                    Mapping(
                        param=(ScalerValue(type="scaler", value_type="int", value="0x1"),),
                        result=VectorValue(type="vector", value_type="int", values=["0x67", "0x2329"]),
                    ),
                ],
            ),
            VectorValue(type="vector", value_type="int", values=["0x66", "0x2328"]),
            Mapping(
                param=(ScalerValue(type="scaler", value_type="int", value="0x0"),),
                result=VectorValue(type="vector", value_type="int", values=["0x66", "0x2328"]),
            ),
            id="found: vector",
        ),
    ],
)
def test_trial_find_target_value(trial: Trial, target: ResultType, expected: Mapping | None) -> None:
    actual = trial.find_target_value(target)
    assert actual == expected


@pytest.mark.parametrize(
    "model",
    [
        TrialModel(
            study_id="my_study_id0",
            trial_id="01",
            timestamp=DT,
            trial_status=TrialStatus.done,
            parameter_space=ParameterAlignedSpaceModel(
                type="aligned",
                axes=[
                    LineSegmentModel(
                        name="x",
                        type="bool",
                        size="0x2",
                        step=1,
                        start=False,
                        ambient_index="0x0",
                        ambient_size="0x2",
                    ),
                ],
                check_lower_filling=True,
            ),
            result_type="scaler",
            result_value_type="bool",
        ),
        TrialModel(
            study_id="my_study_id1",
            trial_id="01",
            timestamp=DT,
            trial_status=TrialStatus.done,
            parameter_space=ParameterAlignedSpaceModel(
                type="aligned",
                axes=[
                    LineSegmentModel(
                        name="x",
                        type="int",
                        size="0x2",
                        step=1,
                        start="0x0",
                        ambient_index="0x0",
                        ambient_size="0x2",
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
                            name="x",
                        ),
                    ),
                    result=ScalerValue(
                        type="scaler",
                        value_type="float",
                        value="0x1.0000000000000p+1",
                        name="r1",
                    ),
                ),
            ],
        ),
        TrialModel(
            study_id="my_study_id2",
            trial_id="02",
            timestamp=DT,
            trial_status=TrialStatus.done,
            parameter_space=ParameterJaggedSpaceModel(
                type="jagged",
                axes_info=[
                    LineSegmentModel(
                        name="x",
                        type="int",
                        size="0x1",
                        start="0x0",
                        step=1,
                        ambient_index="0x0",
                        ambient_size="0x1",
                        is_dummy=True,
                    ),
                ],
                parameters=[("0x1",)],
                ambient_indices=[("0x1",)],
            ),
            result_type="scaler",
            result_value_type="int",
        ),
        TrialModel(
            study_id="my_study_id3",
            trial_id="01",
            timestamp=DT,
            trial_status=TrialStatus.done,
            parameter_space=ParameterJaggedSpaceModel(
                type="jagged",
                axes_info=[
                    LineSegmentModel(
                        name="x",
                        type="int",
                        size="0x1",
                        start="0x0",
                        step=1,
                        ambient_index="0x0",
                        ambient_size="0x1",
                        is_dummy=True,
                    ),
                ],
                parameters=[("0x1",)],
                ambient_indices=[("0x1",)],
            ),
            result_type="scaler",
            result_value_type="int",
            result=[
                Mapping(
                    param=(
                        ScalerValue(
                            type="scaler",
                            value_type="int",
                            value="0x1",
                            name="x",
                        ),
                    ),
                    result=ScalerValue(
                        type="scaler",
                        value_type="int",
                        value="0x2",
                        name="r1",
                    ),
                ),
            ],
        ),
    ],
)
def test_trial_to_model_from_model(model: TrialModel) -> None:
    trial = Trial.from_model(model)
    reconstructed_trial = trial.to_model()
    assert model == reconstructed_trial
