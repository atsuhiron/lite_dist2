from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from lite_dist2.expections import LD2ModelTypeError
from lite_dist2.value_models.point import ParamType, ResultType, ScalerValue, VectorValue
from lite_dist2.value_models.space import ParameterSpace

if TYPE_CHECKING:
    from lite_dist2.type_definitions import RawParamType, RawResultType


class Mapping(BaseModel):
    param: ParamType
    result: ResultType


class TrialStatus(str, Enum):
    not_exec = "not_exec"
    running = "running"
    done = "done"


class Trial(BaseModel):
    study_id: str
    trial_status: TrialStatus
    parameter_space: ParameterSpace
    result_type: Literal["scaler", "vector"]
    result_value_type: Literal["bool", "int", "float"]
    result: list[Mapping] | None = None

    def convert_mappings_from(self, raw_mappings: list[tuple[RawParamType, RawResultType]]) -> list[Mapping]:
        mappings = []
        for raw_param, raw_res in raw_mappings:
            param = self.parameter_space.value_tuple_to_param_type(raw_param)
            result = self._create_result_value(raw_res)
            mappings.append(Mapping(param=param, result=result))
        return mappings

    def set_result(self, mappings: list[Mapping]) -> None:
        self.result = mappings

    def _create_result_value(self, raw_result: RawResultType) -> ResultType:
        match self.result_type:
            case "scaler":
                return ScalerValue.create_from_numeric(raw_result, self.result_value_type)
            case "vector":
                return VectorValue.create_from_numeric(raw_result, self.result_value_type)
            case _:
                raise LD2ModelTypeError(self.result_type)
