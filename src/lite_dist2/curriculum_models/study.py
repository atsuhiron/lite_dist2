from __future__ import annotations

import threading
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

from lite_dist2.common import int2hex, publish_timestamp
from lite_dist2.curriculum_models.study_storage import StudyStorage
from lite_dist2.curriculum_models.trial import Trial, TrialStatus
from lite_dist2.curriculum_models.trial_table import TrialTable, TrialTableModel
from lite_dist2.expections import LD2ModelTypeError
from lite_dist2.study_strategies import StudyStrategyModel
from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.study_strategies.find_exact_study_strategy import FindExactStudyStrategy
from lite_dist2.suggest_strategies import SequentialSuggestStrategy, SuggestStrategyModel
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace, ParameterAlignedSpaceModel

if TYPE_CHECKING:
    from lite_dist2.study_strategies import BaseStudyStrategy
    from lite_dist2.suggest_strategies import BaseSuggestStrategy


class StudyStatus(str, Enum):
    reserved = "reserved"  # TODO: 変える
    running = "running"
    done = "done"


class StudyModel(BaseModel):
    study_id: str
    name: str | None
    required_capacity: set[str]
    status: StudyStatus
    registered_timestamp: datetime
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
        name: str | None,
        required_capacity: set[str],
        status: StudyStatus,
        registered_timestamp: datetime,
        study_strategy: BaseStudyStrategy,
        suggest_strategy: BaseSuggestStrategy,
        parameter_space: ParameterAlignedSpace,
        result_type: Literal["scaler", "vector"],
        result_value_type: Literal["bool", "int", "float"],
        trial_table: TrialTable,
    ) -> None:
        self.study_id = study_id
        self.name = name or self.study_id
        self.required_capacity = required_capacity
        self.status = status
        self.registered_timestamp = registered_timestamp
        self.study_strategy = study_strategy
        self.suggest_strategy = suggest_strategy
        self.parameter_space = parameter_space
        self.result_type = result_type
        self.result_value_type = result_value_type
        self.trial_table = trial_table

        self._table_lock = threading.Lock()

    def update_status(self) -> None:
        if self.trial_table.is_empty():
            self.status = StudyStatus.reserved
            return
        if self.is_done():
            self.status = StudyStatus.done
            return
        self.status = StudyStatus.running

    def is_done(self) -> bool:
        return self.study_strategy.is_done(self.trial_table, self.parameter_space)

    def suggest_next_trial(self, num: int | None) -> Trial | None:
        with self._table_lock:
            parameter_sub_space = self.suggest_strategy.suggest(self.trial_table, num)
            if parameter_sub_space is None:
                return None

            trial = Trial(
                study_id=self.study_id,
                trial_id=self._publish_trial_id(),
                timestamp=publish_timestamp(),
                trial_status=TrialStatus.running,
                parameter_space=parameter_sub_space,
                result_type=self.result_type,
                result_value_type=self.result_value_type,
            )
            self.trial_table.register(trial)
        return trial

    def receipt_trial(self, trial: Trial) -> None:
        if self.trial_table.is_not_defined_aps():
            self.trial_table.init_aps(trial)

        with self._table_lock:
            self.trial_table.receipt_trial(trial.trial_id, trial.result)

    def to_storage(self) -> StudyStorage:
        return StudyStorage(
            study_id=self.study_id,
            name=self.name,
            registered_timestamp=self.registered_timestamp,
            done_timestamp=publish_timestamp(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            result=self.study_strategy.extract_mappings(self.trial_table),
        )

    def to_model(self) -> StudyModel:
        return StudyModel(
            study_id=self.study_id,
            name=self.name,
            required_capacity=self.required_capacity,
            status=self.status,
            registered_timestamp=self.registered_timestamp,
            study_strategy=self.study_strategy.to_model(),
            suggest_strategy=self.suggest_strategy.to_model(),
            parameter_space=self.parameter_space.to_model(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            trial_table=self.trial_table.to_model(),
        )

    def _publish_trial_id(self) -> str:
        return f"{self.study_id}-{int2hex(self.trial_table.count_trial())}"

    @staticmethod
    def _create_study_strategy(model: StudyStrategyModel) -> BaseStudyStrategy:
        match model.type:
            case "all_calculation":
                return AllCalculationStudyStrategy(model.study_strategy_param)
            case "find_exact":
                return FindExactStudyStrategy(model.study_strategy_param)
            case "minimize":
                raise NotImplementedError
            case _:
                raise LD2ModelTypeError(model.type)

    @staticmethod
    def _create_suggest_strategy(model: SuggestStrategyModel, space: ParameterAlignedSpace) -> BaseSuggestStrategy:
        match model.type:
            case "sequential":
                return SequentialSuggestStrategy(model.parameter, space)
            case "random":
                raise NotImplementedError
            case "designated":
                raise NotImplementedError
            case _:
                raise LD2ModelTypeError(model.type)

    @staticmethod
    def from_model(study_model: StudyModel) -> Study:
        parameter_space = ParameterAlignedSpace.from_model(study_model.parameter_space)
        return Study(
            study_id=study_model.study_id,
            name=study_model.name,
            required_capacity=study_model.required_capacity,
            status=study_model.status,
            registered_timestamp=study_model.registered_timestamp,
            study_strategy=Study._create_study_strategy(study_model.study_strategy),
            suggest_strategy=Study._create_suggest_strategy(study_model.suggest_strategy, parameter_space),
            parameter_space=parameter_space,
            result_type=study_model.result_type,
            result_value_type=study_model.result_value_type,
            trial_table=TrialTable.from_model(study_model.trial_table),
        )
