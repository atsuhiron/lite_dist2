import pytest

from lite_dist2.study import TrialTable, TrialTableModel
from lite_dist2.trial import Mapping, TrialModel, TrialStatus
from lite_dist2.value_models.line_segment import LineSegmentModel
from lite_dist2.value_models.point import ScalerValue
from lite_dist2.value_models.space import ParameterAlignedSpaceModel


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
                    trial_status=TrialStatus.running,
                    parameter_space=ParameterAlignedSpaceModel(
                        type="aligned",
                        axes=[
                            LineSegmentModel(
                                type="int",
                                size=10,
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
                    trial_status=TrialStatus.running,
                    parameter_space=ParameterAlignedSpaceModel(
                        type="aligned",
                        axes=[
                            LineSegmentModel(
                                type="int",
                                size=10,
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
                            param=[
                                ScalerValue(
                                    type="scaler",
                                    value_type="int",
                                    value="0x1",
                                    name="p1",
                                ),
                            ],
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
