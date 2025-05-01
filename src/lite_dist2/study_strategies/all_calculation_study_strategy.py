from lite_dist2.study_strategies import BaseStudyStrategy
from lite_dist2.trial_table import TrialTable
from lite_dist2.value_models.space import ParameterAlignedSpace


class AllCalculationStudyStrategy(BaseStudyStrategy):
    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        return trial_table.count_grid() == parameter_space.total

    @staticmethod
    def can_merge() -> bool:
        return True
