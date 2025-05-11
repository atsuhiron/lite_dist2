import uuid
from typing import Literal

from pydantic import BaseModel

from lite_dist2.common import publish_timestamp
from lite_dist2.curriculum_models.study import StudyModel, StudyStatus
from lite_dist2.study_strategies import StudyStrategyModel
from lite_dist2.suggest_strategies import SuggestStrategyModel
from lite_dist2.value_models.aligned_space_registry import ParameterAlignedSpaceRegistry


class StudyRegistry(BaseModel):
    name: str | None
    required_capacity: set[str]
    study_strategy: StudyStrategyModel
    suggest_strategy: SuggestStrategyModel
    parameter_space: ParameterAlignedSpaceRegistry
    result_type: Literal["scaler", "vector"]
    result_value_type: Literal["bool", "int", "float"]

    def to_study_model(self) -> StudyModel:
        return StudyModel(
            study_id=self._publish_study_id(),
            name=self.name,
            required_capacity=self.required_capacity,
            status=StudyStatus.wait,
            registered_timestamp=publish_timestamp(),
            study_strategy=self.study_strategy,
            suggest_strategy=self.suggest_strategy,
            parameter_space=self.parameter_space.to_parameter_aligned_space_model(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
        )

    def _publish_study_id(self) -> str:
        node = hash(self.name) if self.name is not None else hash(self.required_capacity)
        return str(uuid.uuid1(node))
