from __future__ import annotations

from typing import TYPE_CHECKING

from lite_dist2.expections import LD2ModelTypeError, LD2ParameterError
from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.study_strategies.find_exact_study_strategy import FindExactStudyStrategy

if TYPE_CHECKING:
    from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel


def create_study_strategy(model: StudyStrategyModel) -> BaseStudyStrategy:
    param = model.study_strategy_param
    match model.type:
        case "all_calculation":
            return AllCalculationStudyStrategy(param)
        case "find_exact":
            if param is None:
                p = "study_strategy_param"
                et = "missing"
                raise LD2ParameterError(p, et)
            return FindExactStudyStrategy(param)
        case "minimize":
            raise NotImplementedError
        case _:
            raise LD2ModelTypeError(model.type)
