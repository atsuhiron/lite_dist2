from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from lite_dist2.trial_table import TrialTable
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace, ParameterSpace


class SuggestStrategyParam(BaseModel):
    strict_aligned: bool


class SuggestStrategyModel(BaseModel):
    type: Literal["sequential", "random", "designated"]
    parameter: SuggestStrategyParam


class BaseSuggestStrategy(metaclass=abc.ABCMeta):
    def __init__(
        self,
        suggest_parameter: SuggestStrategyParam,
        parameter_space: ParameterAlignedSpace,
    ) -> None:
        self.suggest_parameter = suggest_parameter
        self.parameter_space = parameter_space

    @abc.abstractmethod
    def to_model(self) -> SuggestStrategyModel:
        pass

    @abc.abstractmethod
    def suggest(self, trial_table: TrialTable, max_num: int) -> ParameterSpace:
        pass
