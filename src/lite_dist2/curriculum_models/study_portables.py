from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from lite_dist2.common import publish_timestamp
from lite_dist2.curriculum_models.study_status import StudyStatus
from lite_dist2.curriculum_models.trial import Mapping
from lite_dist2.curriculum_models.trial_table import TrialTableModel
from lite_dist2.study_strategies import StudyStrategyModel
from lite_dist2.suggest_strategies import SuggestStrategyModel
from lite_dist2.value_models.aligned_space import ParameterAlignedSpaceModel
from lite_dist2.value_models.aligned_space_registry import ParameterAlignedSpaceRegistry


class _StudyCommonModel(BaseModel):
    name: str | None
    required_capacity: set[str]
    study_strategy: StudyStrategyModel
    suggest_strategy: SuggestStrategyModel
    result_type: Literal["scalar", "vector"]
    result_value_type: Literal["bool", "int", "float"]


class StudyModel(_StudyCommonModel):
    """
    For save full information
    """

    study_id: str
    status: StudyStatus
    registered_timestamp: datetime
    parameter_space: ParameterAlignedSpaceModel
    trial_table: TrialTableModel = Field(default_factory=TrialTableModel.create_empty)


class StudyRegistry(_StudyCommonModel):
    """
    For registration to curriculum
    """

    parameter_space: ParameterAlignedSpaceRegistry

    def is_valid(self) -> bool:
        is_infinite = any(axis.size is None for axis in self.parameter_space.axes)
        return not (is_infinite and self.study_strategy.type == "all_calculation")

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
        if isinstance(node, int):
            # 下 48 bit だけ取得
            node = node & 0xFFFFFFFFFFFF
        return str(uuid.uuid1(node=node, clock_seq=None))


class StudySummary(_StudyCommonModel):
    """
    For showing summary status
    """

    study_id: str
    status: StudyStatus
    registered_timestamp: datetime
    parameter_space: ParameterAlignedSpaceModel
    total_grids: int | None
    done_grids: int


class StudyStorage(_StudyCommonModel):
    """
    For conclusional result
    """

    study_id: str
    registered_timestamp: datetime
    parameter_space: ParameterAlignedSpaceModel
    done_timestamp: datetime
    results: list[Mapping]
    done_grids: int

    def to_summary(self) -> StudySummary:
        return StudySummary(
            name=self.name,
            study_id=self.study_id,
            required_capacity=self.required_capacity,
            status=StudyStatus.done,
            registered_timestamp=self.registered_timestamp,
            study_strategy=self.study_strategy,
            suggest_strategy=self.suggest_strategy,
            parameter_space=self.parameter_space,
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            total_grids=self.parameter_space.get_total(),
            done_grids=self.done_grids,
        )
