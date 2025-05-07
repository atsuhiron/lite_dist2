from __future__ import annotations

from typing import TYPE_CHECKING

from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel

if TYPE_CHECKING:
    from lite_dist2.study_strategies.base_study_strategy import StudyStrategyParam
    from lite_dist2.trial import Mapping
    from lite_dist2.trial_table import TrialTable
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace


class FindExactStudyStrategy(BaseStudyStrategy):
    def __init__(self, study_strategy_param: StudyStrategyParam | None) -> None:
        super().__init__(study_strategy_param)
        self.found_mapping: Mapping | None = None

    def is_done(self, trial_table: TrialTable, _parameter_space: ParameterAlignedSpace) -> bool:
        if self.found_mapping:
            return True
        self.found_mapping = self._find(trial_table)
        return bool(self.found_mapping)

    def _find(self, trial_table: TrialTable) -> Mapping | None:
        return trial_table.find_target_value(self.study_strategy_param.target_value)

    def extract_mappings(self, trial_table: TrialTable) -> list[Mapping]:
        if not self.found_mapping:
            self.found_mapping = self._find(trial_table)
        if not self.found_mapping:
            return []
        return [self.found_mapping]

    def to_model(self) -> StudyStrategyModel:
        return StudyStrategyModel(
            type="find_exact",
            study_strategy_param=self.study_strategy_param,
        )

    @staticmethod
    def can_merge() -> bool:
        return False
