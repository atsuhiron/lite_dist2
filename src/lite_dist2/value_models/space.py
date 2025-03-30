from __future__ import annotations

import abc
import itertools
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field

from lite_dist2.common import hex2float, hex2int
from lite_dist2.type_definitions import PrimitiveValueType
from lite_dist2.value_models.point import ParamType, ScalerValue

if TYPE_CHECKING:
    from collections.abc import Generator


class LineSegment(BaseModel, metaclass=abc.ABCMeta):
    name: str | None = None
    type: Literal["bool", "int", "float"]

    @abc.abstractmethod
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        pass


class DummyLineSegment(LineSegment):
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        yield from ()


class ParameterRangeBool(LineSegment):
    type: Literal["bool"]
    start: bool
    size: Annotated[int, Field(..., ge=1, le=2)]
    step: Annotated[int, Field(1, ge=1, le=1)]

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        for i in range(self.size):
            yield bool(int(self.start) + i)


class ParameterRangeInt(LineSegment):
    type: Literal["int"]
    start: str
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[int, Field(1, ge=1)]
    step: int = 1

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        s = hex2int(self.start)
        for i in range(self.size):
            yield s + i * self.step


class ParameterRangeFloat(LineSegment):
    type: Literal["float"]
    start: str
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[float, Field(..., gt=0)]

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        s = hex2float(self.start)
        for i in range(self.size):
            yield s + i * self.step


class ParameterSpace(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_dim(self) -> int:
        pass

    @abc.abstractmethod
    def get_total(self) -> int:
        pass

    @abc.abstractmethod
    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        pass

    @abc.abstractmethod
    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        pass


class ParameterAlignedSpace(BaseModel, ParameterSpace):
    axes: list[ParameterRangeBool | ParameterRangeInt | ParameterRangeFloat]

    def get_dims(self) -> tuple[int, ...]:
        return tuple(axis.size for axis in self.axes)

    def get_total(self) -> int:
        n = 1
        for axis in self.axes:
            n *= axis.size
        return n

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from itertools.product(*(axis.grid() for axis in self.axes))

    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        # TODO: type="vector" にも対応させる
        return [
            ScalerValue(type="scaler", value_type=ax.type, value=val, name=ax.name)
            for val, ax in zip(values, self.axes, strict=True)
        ]

    def get_last_dim_size(self) -> int:
        return self.axes[-1].size


class ParameterJaggedSpace(BaseModel, ParameterSpace):
    parameters: list[tuple[PrimitiveValueType, ...]]
    axes_info: list[DummyLineSegment]

    def get_dim(self) -> int:
        return len(self.axes_info)

    def get_total(self) -> int:
        return len(self.parameters)

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from self.parameters

    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        return [
            ScalerValue(type="scaler", value_type=ax.type, value=val, name=ax.name)
            for val, ax in zip(values, self.axes_info, strict=True)
        ]
