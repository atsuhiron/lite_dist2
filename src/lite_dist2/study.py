from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

from lite_dist2.expections import LD2ModelTypeError
from lite_dist2.suggest_strategies import SequentialSuggestStrategy
from lite_dist2.trial import Trial, TrialStatus
from lite_dist2.trial_table import TrialTable, TrialTableModel
from lite_dist2.type_definitions import PrimitiveValueType
from lite_dist2.value_models.point import ResultType
from lite_dist2.value_models.space import ParameterAlignedSpace, ParameterAlignedSpaceModel

if TYPE_CHECKING:
    from lite_dist2.study_strategies import BaseStudyStrategy
    from lite_dist2.suggest_strategies import BaseSuggestStrategy


class StudyStrategyModel(BaseModel):
    type: Literal["all_calculation", "find_exact", "minimize"]
    target_value: ResultType | None

    def create_strategy(self, parameter_space: ParameterAlignedSpace) -> BaseStudyStrategy:
        match self.type:
            case "all_calculation":
                raise NotImplementedError
            case "find_exact":
                raise NotImplementedError
            case "minimize":
                raise NotImplementedError
            case _:
                raise LD2ModelTypeError(self.type)


class SuggestStrategyModel(BaseModel):
    type: Literal["sequential", "random", "designated"]
    parameter: dict[str, PrimitiveValueType | str] | None = None

    def create_strategy(self, parameter_space: ParameterAlignedSpace) -> BaseSuggestStrategy:
        match self.type:
            case "sequential":
                return SequentialSuggestStrategy(self.parameter, parameter_space)
            case "random":
                raise NotImplementedError
            case "designated":
                raise NotImplementedError
            case _:
                raise LD2ModelTypeError(self.type)


class StudyModel(BaseModel):
    study_id: str
    name: str
    study_strategy: StudyStrategyModel
    suggest_strategy: SuggestStrategyModel
    parameter_space: ParameterAlignedSpaceModel
    result_type: Literal["scaler", "vector"]
    result_value_type: Literal["bool", "int", "float"]
    trial_table: TrialTableModel = Field(default_factory=TrialTableModel.create_empty)


class Study:
    def __init__(
        self,
        study_id: str,
        name: str,
        study_strategy_model: StudyStrategyModel,
        suggest_strategy_model: SuggestStrategyModel,
        parameter_space: ParameterAlignedSpace,
        result_type: Literal["scaler", "vector"],
        result_value_type: Literal["bool", "int", "float"],
        trial_table: TrialTable,
    ) -> None:
        self.study_id = study_id
        self.name = name
        self.study_strategy_model = study_strategy_model
        self.suggest_strategy_model = suggest_strategy_model
        self.parameter_space = parameter_space
        self.result_type = result_type
        self.result_value_type = result_value_type
        self.trial_table = trial_table

        self.study_strategy = study_strategy_model.create_strategy(self.parameter_space)
        self.suggest_strategy = suggest_strategy_model.create_strategy(self.parameter_space)

    def is_done(self) -> bool:
        return self.study_strategy.is_done(self.trial_table, self.parameter_space)

    def suggest_next_trial(self, num: int | None) -> Trial:
        parameter_sub_space = self.suggest_strategy.suggest(self.trial_table, num)
        return Trial(
            study_id=self.study_id,
            trial_status=TrialStatus.running,
            parameter_space=parameter_sub_space,
            result_type=self.result_type,
            result_value_type=self.result_value_type,
        )

    def to_model(self) -> StudyModel:
        return StudyModel(
            study_id=self.study_id,
            name=self.name,
            study_strategy=self.study_strategy_model,
            suggest_strategy=self.suggest_strategy_model,
            parameter_space=self.parameter_space.to_model(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            trial_table=self.trial_table.to_model(),
        )

    @staticmethod
    def from_model(study_model: StudyModel) -> Study:
        return Study(
            study_id=study_model.study_id,
            name=study_model.name,
            study_strategy_model=study_model.study_strategy,
            suggest_strategy_model=study_model.suggest_strategy,
            parameter_space=ParameterAlignedSpace.from_model(study_model.parameter_space),
            result_type=study_model.result_type,
            result_value_type=study_model.result_value_type,
            trial_table=TrialTable.from_model(study_model.trial_table),
        )
