from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

from lite_dist2.trial import Trial
from lite_dist2.value_models.point import ResultType

if TYPE_CHECKING:
    from lite_dist2.study_strategies import BaseStudyStrategy


class StudyStrategyType(str, Enum):
    all_calculation = "all_calculation"
    find_exact = "find_exact"
    minimize = "minimize"


class SuggestMethod(str, Enum):
    sequential = "sequential"
    random = "random"
    designated = "designated"


class StudyStrategyModel(BaseModel):
    type: Literal["all_calculation", "find_exact", "minimize"]
    target_value: ResultType | None

    def create_strategy(self) -> BaseStudyStrategy:
        raise NotADirectoryError


class TrialTable(BaseModel):
    trials: list[Trial]

    @staticmethod
    def create_empty() -> TrialTable:
        return TrialTable(trials=[])


class StudyModel(BaseModel):
    study_id: str
    name: str
    study_strategy: StudyStrategyModel
    trial_table: TrialTable | None = Field(default_factory=TrialTable.create_empty)


class Study:
    def __init__(self, study_model: StudyModel) -> None:
        self.study_id = study_model.study_id
        self.name = study_model.name
        self.study_strategy = study_model.study_strategy.create_strategy()
        self.trial_table = study_model.trial_table

    def is_done(self) -> bool:
        return self.trial_table.is_done(self.study_strategy)

    def suggest_next_trial(self) -> Trial:
        return self.trial_table.suggest_next_trial()
