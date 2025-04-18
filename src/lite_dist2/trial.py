from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from lite_dist2.expections import LD2ModelTypeError, LD2UndefinedError
from lite_dist2.value_models.point import ParamType, ResultType, ScalerValue, VectorValue
from lite_dist2.value_models.space import (
    ParameterAlignedSpace,
    ParameterAlignedSpaceModel,
    ParameterJaggedSpace,
    ParameterJaggedSpaceModel,
    ParameterSpace,
)

if TYPE_CHECKING:
    from lite_dist2.type_definitions import RawParamType, RawResultType


class Mapping(BaseModel):
    param: ParamType
    result: ResultType


class TrialStatus(str, Enum):
    not_exec = "not_exec"
    running = "running"
    done = "done"


class TrialModel(BaseModel):
    study_id: str
    trial_status: TrialStatus
    parameter_space: ParameterAlignedSpaceModel | ParameterJaggedSpaceModel
    result_type: Literal["scaler", "vector"]
    result_value_type: Literal["bool", "int", "float"]
    result: list[Mapping] | None = None


class Trial:
    def __init__(
        self,
        study_id: str,
        trial_status: TrialStatus,
        parameter_space: ParameterSpace,
        result_type: Literal["scaler", "vector"],
        result_value_type: Literal["bool", "int", "float"],
        result: list[Mapping] | None = None,
    ) -> None:
        self.study_id = study_id
        self.trial_status = trial_status
        self.parameter_space = parameter_space
        self.result_type = result_type
        self.result_value_type = result_value_type
        self.result = result

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

    def to_model(self) -> TrialModel:
        return TrialModel(
            study_id=self.study_id,
            trial_status=self.trial_status,
            parameter_space=self.parameter_space.to_model(),
            result_type=self.result_type,
            result_value_type=self.result_value_type,
            result=self.result,
        )

    @staticmethod
    def from_model(model: TrialModel) -> Trial:
        match model.parameter_space.type:
            case "aligned":
                parameter_space = ParameterAlignedSpace.from_model(model.parameter_space)
            case "jagged":
                parameter_space = ParameterJaggedSpace.from_model(model.parameter_space)
            case _:
                raise LD2UndefinedError(model.parameter_space.type)
        return Trial(
            study_id=model.study_id,
            trial_status=model.trial_status,
            parameter_space=parameter_space,
            result_type=model.result_type,
            result_value_type=model.result_value_type,
            result=model.result,
        )
