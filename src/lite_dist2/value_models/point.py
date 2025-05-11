from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from lite_dist2.common import numerize, portablize
from lite_dist2.type_definitions import PortableValueType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lite_dist2.type_definitions import PrimitiveValueType, RawResultType


class BasePointValue(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def numerize(self) -> PrimitiveValueType | list[PrimitiveValueType]:
        pass

    @abc.abstractmethod
    def equal_to(self, other: BasePointValue) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def create_from_numeric(
        raw_result_value: RawResultType,
        value_type: Literal["bool", "int", "float"],
        name: str | None = None,
    ) -> BasePointValue:
        pass


class ScalerValue(BaseModel, BasePointValue):
    type: Literal["scaler"]
    value_type: Literal["bool", "int", "float"]
    value: PortableValueType
    name: str | None = None

    def numerize(self) -> PrimitiveValueType:
        return numerize(self.value_type, self.value)

    def equal_to(self, other: BasePointValue) -> bool:
        if not isinstance(other, ScalerValue):
            return False
        return self.value_type == other.value_type and self.value == other.value

    @staticmethod
    def create_from_numeric(
        raw_result_value: RawResultType,
        value_type: Literal["bool", "int", "float"],
        name: str | None = None,
    ) -> ScalerValue:
        val = portablize(value_type, raw_result_value)
        return ScalerValue(type="scaler", value_type=value_type, value=val, name=name)


class VectorValue(BaseModel, BasePointValue):
    type: Literal["vector"]
    value_type: Literal["bool", "int", "float"]
    values: list[PortableValueType]
    name: str | None = None

    def numerize(self) -> list[PrimitiveValueType]:
        return [numerize(self.value_type, v) for v in self.values]

    def equal_to(self, other: BasePointValue) -> bool:
        if not isinstance(other, VectorValue):
            return False
        return self.value_type == other.value_type and self.values == other.values

    @staticmethod
    def create_from_numeric(
        raw_result_value: Iterable[RawResultType],
        value_type: Literal["bool", "int", "float"],
        name: str | None = None,
    ) -> VectorValue:
        val = [portablize(value_type, rv) for rv in raw_result_value]
        return VectorValue(type="vector", value_type=value_type, values=val, name=name)


type ParamType = tuple[ScalerValue, ...]
type ResultType = ScalerValue | VectorValue
