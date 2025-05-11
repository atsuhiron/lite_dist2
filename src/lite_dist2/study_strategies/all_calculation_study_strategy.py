from __future__ import annotations

from typing import TYPE_CHECKING

from lite_dist2.curriculum_models.trial import TrialStatus
from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel

if TYPE_CHECKING:
    from lite_dist2.curriculum_models.trial import Mapping
    from lite_dist2.curriculum_models.trial_table import TrialTable
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace


class AllCalculationStudyStrategy(BaseStudyStrategy):
    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        return trial_table.count_grid() == parameter_space.total

    def extract_mappings(self, trial_table: TrialTable) -> list[Mapping]:
        mappings = []
        for trial in trial_table.trials:
            if trial.trial_status != TrialStatus.done:
                continue
            mappings.extend(trial.result or [])
        return mappings

    def to_model(self) -> StudyStrategyModel:
        return StudyStrategyModel(
            type="all_calculation",
            study_strategy_param=self.study_strategy_param,
        )
