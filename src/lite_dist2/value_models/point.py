from __future__ import annotations

import abc
from typing import Iterable, Literal

from pydantic import BaseModel

from lite_dist2.common import float2hex, hex2float, hex2int, int2hex
from lite_dist2.expections import LD2InvalidParameterError
from lite_dist2.type_definitions import PrimitiveValueType, RawResultType


class BasePointValue(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def numerize(self) -> PrimitiveValueType | list[PrimitiveValueType]:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_from_numeric(
            raw_result_value: RawResultType,
            value_type: Literal["bool", "int", "float"],
            name: str | None = None
    ) -> BasePointValue:
        pass


class ScalerValue(BaseModel, BasePointValue):
    type: Literal["scaler"]
    value_type: Literal["bool", "int", "float"]
    value: bool | str
    name: str | None = None

    def numerize(self) -> PrimitiveValueType:
        match self.value_type:
            case "bool":
                return self.value
            case "int":
                return hex2int(self.value)
            case "float":
                return hex2float(self.value)
            case _:
                raise LD2InvalidParameterError(f"Unknown type: {self.type}")

    @staticmethod
    def create_from_numeric(
            raw_result_value: RawResultType,
            value_type: Literal["bool", "int", "float"],
            name: str | None = None
    ) -> ScalerValue:
        pass
        match value_type:
            case "bool":
                val = raw_result_value
                return ScalerValue(type="scaler", value_type="bool", value=val, name=name)
            case "int":
                val = int2hex(raw_result_value)
                return ScalerValue(type="scaler", value_type="int", value=val, name=name)
            case "float":
                val = float2hex(raw_result_value)
                return ScalerValue(type="scaler", value_type="float", value=val, name=name)
            case _:
                raise LD2InvalidParameterError(f"Unknown type: {value_type}")


class VectorValue(BaseModel, BasePointValue):
    type: Literal["vector"]
    value_type: Literal["bool", "int", "float"]
    values: list[bool | str]
    name: str | None = None

    def numerize(self) -> list[PrimitiveValueType]:
        match self.value_type:
            case "bool":
                return self.values
            case "int":
                return [hex2int(v) for v in self.values]
            case "float":
                return [hex2float(v) for v in self.values]
            case _:
                raise LD2InvalidParameterError(f"Unknown type: {self.type}")

    @staticmethod
    def create_from_numeric(
            raw_result_value: Iterable[RawResultType],
            value_type: Literal["bool", "int", "float"],
            name: str | None = None
    ) -> VectorValue:
        pass
        match value_type:
            case "bool":
                val = [v for v in raw_result_value]
                return VectorValue(type="vector", value_type="bool", values=val, name=name)
            case "int":
                val = [int2hex(v) for v in raw_result_value]
                return VectorValue(type="vector", value_type="int", values=val, name=name)
            case "float":
                val = [float2hex(v) for v in raw_result_value]
                return VectorValue(type="vector", value_type="float", values=val, name=name)
            case _:
                raise LD2InvalidParameterError(f"Unknown type: {value_type}")


type ParamType = list[ScalerValue]
type ResultType = ScalerValue | VectorValue
