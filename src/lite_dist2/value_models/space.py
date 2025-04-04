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
    size: int
    ambient_index: int

    @abc.abstractmethod
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        pass

    @abc.abstractmethod
    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        pass

    def end_index(self) -> int:
        return self.ambient_index + self.size - 1


class DummyLineSegment(LineSegment):
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        yield from ()

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        yield from ()


class ParameterRangeBool(LineSegment):
    type: Literal["bool"]
    start: bool
    size: Annotated[int, Field(..., ge=1, le=2)]
    step: Annotated[int, Field(1, ge=1, le=1)]

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        for i in range(self.size):
            yield bool(int(self.start) + i)

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        for i in range(self.size):
            yield i, bool(int(self.start) + i)


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

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        s = hex2int(self.start)
        for i in range(self.size):
            yield i, s + i * self.step


class ParameterRangeFloat(LineSegment):
    type: Literal["float"]
    start: str
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[float, Field(..., gt=0)]

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        s = hex2float(self.start)
        for i in range(self.size):
            yield s + i * self.step

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        s = hex2float(self.start)
        for i in range(self.size):
            yield i, s + i * self.step


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
    def indexed_grid(self) -> Generator[tuple[tuple[int, PrimitiveValueType], ...], None, None]:
        pass

    @abc.abstractmethod
    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        pass

    @abc.abstractmethod
    def derived_by_same_ambient_space_with(self, other: ParameterSpace) -> bool:
        pass


class ParameterAlignedSpace(BaseModel, ParameterSpace):
    axes: list[ParameterRangeBool | ParameterRangeInt | ParameterRangeFloat]  # larger index, deeper dimension
    filling_dim: list[bool]

    def get_dim(self) -> int:
        return len(self.get_dims())

    def get_dims(self) -> tuple[int, ...]:
        return tuple(axis.size for axis in self.axes)

    def get_total(self) -> int:
        n = 1
        for axis in self.axes:
            n *= axis.size
        return n

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from itertools.product(*(axis.grid() for axis in self.axes))

    def indexed_grid(self) -> Generator[tuple[tuple[int, PrimitiveValueType], ...], None, None]:
        yield from itertools.product(*(axis.indexed_grid() for axis in self.axes))

    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        # TODO: type="vector" にも対応させる
        return [
            ScalerValue(type="scaler", value_type=ax.type, value=val, name=ax.name)
            for val, ax in zip(values, self.axes, strict=True)
        ]

    def derived_by_same_ambient_space_with(self, other: ParameterSpace) -> bool:
        if not isinstance(other, ParameterAlignedSpace):
            return False
        if len(self.axes) != len(other.axes):
            return False
        return all((s.name == o.name) and (s.type == o.type) for s, o in zip(self.axes, other.axes, strict=True))

    def get_last_dim_size(self) -> int:
        return self.axes[-1].size

    def can_merge(self, other: ParameterAlignedSpace, target_dim: int) -> bool:
        if not self.derived_by_same_ambient_space_with(other):
            # 同じ母空間から誘導されたものでなければ False
            return False

        if self.filling_dim != other.filling_dim:
            # 各次元の占有状態が同じでなければ False
            return False

        if self.filling_dim[target_dim]:
            # 対象の次元を占有していたら False
            return False
        if not all(self.filling_dim[target_dim + 1 :]):
            # 対象の次元より深い次元を占有していなければ False
            # 最深次元(空リスト)であれば True
            return False

        self_axis = self.axes[target_dim]
        other_axis = other.axes[target_dim]
        if self_axis.ambient_index < other_axis.ambient_index:
            smaller = self_axis
            larger = other_axis
        else:
            smaller = other_axis
            larger = self_axis

        return smaller.end_index() + 1 >= larger.ambient_index


class ParameterJaggedSpace(BaseModel, ParameterSpace):
    parameters: list[tuple[PrimitiveValueType, ...]]
    axes_info: list[DummyLineSegment]

    def get_dim(self) -> int:
        return len(self.axes_info)

    def get_total(self) -> int:
        return len(self.parameters)

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from self.parameters

    def indexed_grid(self) -> Generator[tuple[tuple[int, PrimitiveValueType], ...], None, None]:
        raise NotImplementedError  # 到達しないはず??

    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        return [
            ScalerValue(type="scaler", value_type=ax.type, value=val, name=ax.name)
            for val, ax in zip(values, self.axes_info, strict=True)
        ]

    def derived_by_same_ambient_space_with(self, other: ParameterSpace) -> bool:
        if isinstance(other, ParameterJaggedSpace):
            return self.axes_info == other.axes_info
        return False


if __name__ == "__main__":
    pri1 = ParameterRangeInt(name="x", type="int", start="ff", size=4, ambient_index=0)
    pri2 = ParameterRangeInt(name="y", type="int", start="fff", size=6, ambient_index=0)
    space = ParameterAlignedSpace(axes=[pri1, pri2], filling_dim=[False, False])
    for g in space.grid():
        print(g)  # noqa: T201
