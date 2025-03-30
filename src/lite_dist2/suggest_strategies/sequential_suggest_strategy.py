from __future__ import annotations

from typing import TYPE_CHECKING

from lite_dist2.suggest_strategies import BaseSuggestStrategy

if TYPE_CHECKING:
    from lite_dist2.study import TrialTable
    from lite_dist2.type_definitions import PrimitiveValueType
    from lite_dist2.value_models.space import ParameterAlignedSpace, ParameterSpace


class SequentialSuggestStrategy(BaseSuggestStrategy):
    def __init__(
        self,
        suggest_parameter: dict[str, PrimitiveValueType | str],
        parameter_space: ParameterAlignedSpace,
    ) -> None:
        super().__init__(suggest_parameter, parameter_space)
        self.strict_aligned = self.suggest_parameter.get("strict_aligned", False)

    def suggest(self, trial_table: TrialTable, num: int | None) -> ParameterSpace:
        dims: tuple[int, ...] = self.parameter_space.get_dims()
        if len(dims) == 1:
            return self.suggest_1dim(trial_table, num)

        # TODO: もうちょっと考えればもっと多くの場合で True にできる
        if self.strict_aligned:
            pass

    def suggest_1dim(self, trial_table: TrialTable, num: int | None) -> ParameterSpace:
        pass
