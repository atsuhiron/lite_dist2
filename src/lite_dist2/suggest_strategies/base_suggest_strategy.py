from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from lite_dist2.curriculum_models.trial_table import TrialTable
    from lite_dist2.value_models.space_type import ParameterSpaceType


class SuggestStrategyParam(BaseModel):
    strict_aligned: bool


class SuggestStrategyModel(BaseModel):
    type: Literal["sequential", "random", "designated"]
    suggest_strategy_param: SuggestStrategyParam


class BaseSuggestStrategy(abc.ABC):
    @abc.abstractmethod
    def to_model(self) -> SuggestStrategyModel:
        pass

    @abc.abstractmethod
    def suggest(self, trial_table: TrialTable, max_num: int) -> ParameterSpaceType | None:
        pass
