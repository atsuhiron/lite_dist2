from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from pydantic import BaseModel

from lite_dist2.value_models.point import ResultType

if TYPE_CHECKING:
    from lite_dist2.study import TrialTable
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace


class StudyStrategyParam(BaseModel):
    target_value: ResultType


class BaseStudyStrategy(metaclass=abc.ABCMeta):
    def __init__(self, study_strategy_param: StudyStrategyParam | None) -> None:
        self.study_strategy_param = study_strategy_param

    @abc.abstractmethod
    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def can_merge() -> bool:
        pass
