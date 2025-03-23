from __future__ import annotations

from pydantic import BaseModel

from lite_dist2.type_definitions import ParamType, ResultType
from lite_dist2.value_models.space import ParameterSpace


class Mapping(BaseModel):
    param: ParamType
    result: ResultType


class Trial(BaseModel):
    parameter_space: ParameterSpace
    result: list[Mapping] | None = None

    def create_new_with(self, mappings: list[Mapping]) -> Trial:
        return Trial(parameter_space=self.parameter_space, result=mappings)
