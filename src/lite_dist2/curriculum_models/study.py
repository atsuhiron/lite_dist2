from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Literal

from lite_dist2.common import int2hex, publish_timestamp
from lite_dist2.curriculum_models.study_portables import StudyModel, StudyStorage, StudySummary
from lite_dist2.curriculum_models.study_status import StudyStatus
from lite_dist2.curriculum_models.trial import Trial, TrialStatus
from lite_dist2.curriculum_models.trial_table import TrialTable
from lite_dist2.expections import LD2ModelTypeError
from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.study_strategies.find_exact_study_strategy import FindExactStudyStrategy
from lite_dist2.suggest_strategies import SequentialSuggestStrategy, SuggestStrategyModel
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace

if TYPE_CHECKING:
    from datetime import datetime

    from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel
    from lite_dist2.suggest_strategies import BaseSuggestStrategy


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
        if self.is_done():
            self.status = StudyStatus.done
            return

    def is_done(self) -> bool:
        return self.study_strategy.is_done(self.trial_table, self.parameter_space)

    def suggest_next_trial(self, num: int | None) -> Trial | None:
        with self._table_lock:
            self.status = StudyStatus.running

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
        if self.trial_table.is_not_defined_aps():
            self.trial_table.init_aps(trial)
        return trial

    def receipt_trial(self, trial: Trial) -> None:
        with self._table_lock:
            self.trial_table.receipt_trial(trial.trial_id, trial.result)
            self.trial_table.simplify_aps()

    def check_timeout_trial(self, now: datetime, timeout_seconds: int) -> list[str]:
        return self.trial_table.check_timeout_trial(now, timeout_seconds)

    def to_storage(self) -> StudyStorage:
        return StudyStorage(
            study_id=self.study_id,
            name=self.name,
            required_capacity=self.required_capacity,
            registered_timestamp=self.registered_timestamp,
            study_strategy=self.study_strategy.to_model(),
            suggest_strategy=self.suggest_strategy.to_model(),
            parameter_space=self.parameter_space.to_model(),
            done_timestamp=publish_timestamp(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            result=self.study_strategy.extract_mappings(self.trial_table),
            done_grids=self.trial_table.count_grid(),
        )

    def to_summary(self) -> StudySummary:
        done_grids = sum(trial.parameter_space.get_total() for trial in self.trial_table.trials)
        return StudySummary(
            name=self.name,
            study_id=self.study_id,
            required_capacity=self.required_capacity,
            status=self.status,
            registered_timestamp=self.registered_timestamp,
            study_strategy=self.study_strategy.to_model(),
            suggest_strategy=self.suggest_strategy.to_model(),
            parameter_space=self.parameter_space.to_model(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            total_grids=self.parameter_space.total,
            done_grids=done_grids,
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
