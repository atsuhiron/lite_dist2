from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lite_dist2.study import TrialTable
    from lite_dist2.value_models.point import ResultType


class BaseStudyStrategy(metaclass=abc.ABCMeta):
    def __init__(self, target_value: ResultType) -> None:
        self.target_value = target_value

    @abc.abstractmethod
    def is_done(self, trial_table: TrialTable) -> bool:
        pass
