from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lite_dist2.study import TrialTable
    from lite_dist2.value_models.space import ParameterSpace


class BaseSuggestStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def suggest(self, trial_table: TrialTable, parameter_space: ParameterSpace) -> ParameterSpace:
        pass
