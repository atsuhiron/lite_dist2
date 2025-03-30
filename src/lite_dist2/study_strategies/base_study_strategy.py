from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lite_dist2.study import TrialTable
    from lite_dist2.value_models.point import ResultType
    from lite_dist2.value_models.space import ParameterSpace


class BaseStudyStrategy(metaclass=abc.ABCMeta):
    def __init__(self, target_value: ResultType, parameter_space: ParameterSpace) -> None:
        self.target_value = target_value
        self.parameter_space = parameter_space

    @abc.abstractmethod
    def is_done(self, trial_table: TrialTable, parameter_space: ParameterSpace) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def can_merge() -> bool:
        pass
