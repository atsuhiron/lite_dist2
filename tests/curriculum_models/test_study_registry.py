from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from lite_dist2.curriculum_models.study import StudyModel, StudyStatus
from lite_dist2.curriculum_models.study_registry import StudyRegistry
from lite_dist2.study_strategies import StudyStrategyModel
from lite_dist2.study_strategies.base_study_strategy import StudyStrategyParam
from lite_dist2.suggest_strategies import SuggestStrategyModel
from lite_dist2.suggest_strategies.base_suggest_strategy import SuggestStrategyParam
from lite_dist2.value_models.aligned_space import ParameterAlignedSpaceModel
from lite_dist2.value_models.aligned_space_registry import LineSegmentRegistry, ParameterAlignedSpaceRegistry
from lite_dist2.value_models.line_segment import LineSegmentModel
from lite_dist2.value_models.point import VectorValue
from tests.const import DT

if TYPE_CHECKING:
    from pytest_mock.plugin import MockerFixture


@pytest.mark.parametrize(
    ("registry", "expected"),
    [
        (
            StudyRegistry(
                name="test_registry",
                required_capacity={"test"},
                study_strategy=StudyStrategyModel(
                    type="find_exact",
                    study_strategy_param=StudyStrategyParam(
                        target_value=VectorValue(
                            type="vector",
                            value_type="int",
                            name="test_target",
                            values=["0x0", "0x1", "0x2"],
                        ),
                    ),
                ),
                suggest_strategy=SuggestStrategyModel(
                    type="sequential",
                    parameter=SuggestStrategyParam(strict_aligned=True),
                ),
                parameter_space=ParameterAlignedSpaceRegistry(
                    type="aligned",
                    axes=[
                        LineSegmentRegistry(name="x", type="int", size="0x64", step="0x2", start="0x0"),
                        LineSegmentRegistry(name="y", type="float", size="0x64", step="0x1.0p-1", start="0x0.0p+0"),
                    ],
                ),
                result_type="vector",
                result_value_type="int",
            ),
            StudyModel(
                study_id="test_study_id",
                name="test_registry",
                required_capacity={"test"},
                status=StudyStatus.wait,
                registered_timestamp=DT,
                study_strategy=StudyStrategyModel(
                    type="find_exact",
                    study_strategy_param=StudyStrategyParam(
                        target_value=VectorValue(
                            type="vector",
                            value_type="int",
                            name="test_target",
                            values=["0x0", "0x1", "0x2"],
                        ),
                    ),
                ),
                suggest_strategy=SuggestStrategyModel(
                    type="sequential",
                    parameter=SuggestStrategyParam(strict_aligned=True),
                ),
                parameter_space=ParameterAlignedSpaceModel(
                    type="aligned",
                    axes=[
                        LineSegmentModel(
                            name="x",
                            type="int",
                            size="0x64",
                            step="0x2",
                            start="0x0",
                            ambient_size="0x64",
                            ambient_index="0x0",
                        ),
                        LineSegmentModel(
                            name="y",
                            type="float",
                            size="0x64",
                            step="0x1.0p-1",
                            start="0x0.0p+0",
                            ambient_size="0x64",
                            ambient_index="0x0",
                        ),
                    ],
                    check_lower_filling=True,
                ),
                result_type="vector",
                result_value_type="int",
            ),
        ),
    ],
)
def test_study_registry_to_study_model(registry: StudyRegistry, expected: StudyModel, mocker: MockerFixture) -> None:
    mocker.patch(
        "lite_dist2.curriculum_models.study_registry.StudyRegistry._publish_study_id",
        return_value="test_study_id",
    )
    mocker.patch("lite_dist2.curriculum_models.study_registry.publish_timestamp", return_value=DT)
    actual = registry.to_study_model()
    assert actual == expected
