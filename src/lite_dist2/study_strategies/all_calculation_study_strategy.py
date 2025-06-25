from __future__ import annotations

from typing import TYPE_CHECKING

from lite_dist2.curriculum_models.mapping import MappingsStorage
from lite_dist2.expections import LD2NotDoneError
from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel

if TYPE_CHECKING:
    from lite_dist2.curriculum_models.trial_table import TrialTable
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace


class AllCalculationStudyStrategy(BaseStudyStrategy):
    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        return trial_table.count_grid() == parameter_space.total

    def extract_mappings(self, trial_table: TrialTable) -> MappingsStorage:
        if not trial_table.trials:
            raise LD2NotDoneError
        mappings = trial_table.trials[0].result
        if mappings is None:
            raise LD2NotDoneError
        first = mappings[0]

        params = tuple(param.to_dummy() for param in first.params)
        result = first.result.to_dummy()

        try:
            values = [mapping.to_tuple() for trial in trial_table.trials for mapping in trial.result]
        except TypeError as e:
            raise LD2NotDoneError from e
        return MappingsStorage(params_info=params, result_info=result, values=values)

    def to_model(self) -> StudyStrategyModel:
        return StudyStrategyModel(
            type="all_calculation",
            study_strategy_param=self.study_strategy_param,
        )
