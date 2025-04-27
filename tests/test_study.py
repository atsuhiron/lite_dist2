import pytest

from lite_dist2.study import Study, StudyModel, StudyStrategyModel, SuggestStrategyModel
from lite_dist2.trial import Mapping, TrialModel, TrialStatus
from lite_dist2.trial_table import TrialTableModel
from lite_dist2.value_models.line_segment import LineSegmentModel
from lite_dist2.value_models.point import ScalerValue
from lite_dist2.value_models.space import ParameterAlignedSpaceModel


@pytest.mark.parametrize(
    "model",
    [
        pytest.param(
            StudyModel(
                study_id="01",
                name="s1",
                study_strategy=StudyStrategyModel(type="all_calculation", study_strategy_param=None),
                suggest_strategy=SuggestStrategyModel(type="sequential"),
                parameter_space=ParameterAlignedSpaceModel(
                    type="aligned",
                    axes=[
                        LineSegmentModel(
                            name="x",
                            type="int",
                            size=100,
                            step=1,
                            start="0x0",
                            ambient_size="0x64",
                            ambient_index="0x0",
                        ),
                        LineSegmentModel(
                            name="y",
                            type="int",
                            size=100,
                            step=1,
                            start="0x0",
                            ambient_size="0x64",
                            ambient_index="0x0",
                        ),
                    ],
                    check_lower_filling=True,
                ),
                result_type="scaler",
                result_value_type="int",
                trial_table=TrialTableModel(
                    trials=[
                        TrialModel(
                            study_id="01",
                            trial_status=TrialStatus.done,
                            parameter_space=ParameterAlignedSpaceModel(
                                type="aligned",
                                axes=[
                                    LineSegmentModel(
                                        name="x",
                                        type="int",
                                        size=1,
                                        step=1,
                                        start="0x0",
                                        ambient_size="0x64",
                                        ambient_index="0x0",
                                    ),
                                    LineSegmentModel(
                                        name="y",
                                        type="int",
                                        size=2,
                                        step=1,
                                        start="0x0",
                                        ambient_size="0x64",
                                        ambient_index="0x0",
                                    ),
                                ],
                                check_lower_filling=True,
                            ),
                            result_type="scaler",
                            result_value_type="float",
                            result=[
                                Mapping(
                                    param=(
                                        ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                        ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                    ),
                                    result=ScalerValue(
                                        type="scaler",
                                        value_type="float",
                                        value="0x1.0000000000000p-1",
                                    ),
                                ),
                                Mapping(
                                    param=(
                                        ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                        ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                    ),
                                    result=ScalerValue(
                                        type="scaler",
                                        value_type="float",
                                        value="0x1.0000000000000p-2",
                                    ),
                                ),
                            ],
                        ),
                        TrialModel(
                            study_id="01",
                            trial_status=TrialStatus.running,
                            parameter_space=ParameterAlignedSpaceModel(
                                type="aligned",
                                axes=[
                                    LineSegmentModel(
                                        name="x",
                                        type="int",
                                        size=1,
                                        step=1,
                                        start="0x0",
                                        ambient_size="0x64",
                                        ambient_index="0x0",
                                    ),
                                    LineSegmentModel(
                                        name="y",
                                        type="int",
                                        size=2,
                                        step=1,
                                        start="0x2",
                                        ambient_size="0x64",
                                        ambient_index="0x2",
                                    ),
                                ],
                                check_lower_filling=True,
                            ),
                            result_type="scaler",
                            result_value_type="float",
                        ),
                    ],
                    aggregated_parameter_space={
                        -1: [],
                        0: [
                            ParameterAlignedSpaceModel(
                                type="aligned",
                                axes=[
                                    LineSegmentModel(
                                        name="x",
                                        type="int",
                                        size=1,
                                        step=1,
                                        start="0x0",
                                        ambient_size="0x64",
                                        ambient_index="0x0",
                                    ),
                                    LineSegmentModel(
                                        name="y",
                                        type="int",
                                        size=2,
                                        step=1,
                                        start="0x0",
                                        ambient_size="0x64",
                                        ambient_index="0x0",
                                    ),
                                ],
                                check_lower_filling=True,
                            ),
                        ],
                    },
                ),
            ),
            id="full_definition",
        ),
    ],
)
def test_study_to_model_from_model(model: StudyModel) -> None:
    study = Study.from_model(model)
    reconstructed = study.to_model()
    assert model == reconstructed
