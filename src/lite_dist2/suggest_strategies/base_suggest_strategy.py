from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lite_dist2.study import TrialTable
    from lite_dist2.type_definitions import PrimitiveValueType
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace, ParameterSpace


class BaseSuggestStrategy(metaclass=abc.ABCMeta):
    def __init__(
        self,
        suggest_parameter: dict[str, PrimitiveValueType | str],
        parameter_space: ParameterAlignedSpace,
    ) -> None:
        self.suggest_parameter = suggest_parameter
        self.parameter_space = parameter_space

    @abc.abstractmethod
    def suggest(self, trial_table: TrialTable, max_num: int) -> ParameterSpace:
        pass
