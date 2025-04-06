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
    ambient_size: str | None = None

    @abc.abstractmethod
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        pass

    @abc.abstractmethod
    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        pass

    @abc.abstractmethod
    def get_step(self) -> PrimitiveValueType:
        pass

    def derived_by_same_ambient_space_with(self, other: LineSegment) -> bool:
        return (
            (self.name == other.name)
            and (self.type == other.type)
            and (self.get_step() == other.get_step())
            and (self.ambient_size == other.ambient_size)
        )

    def can_merge(self, other: LineSegment) -> bool:
        if self.ambient_index < other.ambient_index:
            smaller = self
            larger = other
        else:
            smaller = other
            larger = self

        return smaller.end_index() + 1 >= larger.ambient_index

    @abc.abstractmethod
    def merge(self, other: LineSegment) -> LineSegment:
        pass

    def end_index(self) -> int:
        return self.ambient_index + self.size - 1

    def is_universal(self) -> bool:
        if self.ambient_size is None:
            return False
        return self.size == hex2int(self.ambient_size)


class DummyLineSegment(LineSegment):
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        yield from ()

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        yield from ()

    def get_step(self) -> PrimitiveValueType:
        return 1

    def can_merge(self, _other: LineSegment) -> bool:
        return False

    def merge(self, _other: LineSegment) -> LineSegment:
        return self


class ParameterRangeBool(LineSegment):
    type: Literal["bool"]
    start: bool
    size: Annotated[int, Field(..., ge=1, le=2)]
    step: Annotated[int, Field(1, ge=1, le=1)]
    step: int = 1

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        for i in range(self.size):
            yield bool(int(self.start) + i)

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        for i in range(self.size):
            yield i, bool(int(self.start) + i)

    def get_step(self) -> PrimitiveValueType:
        return self.step

    def merge(self, other: ParameterRangeBool) -> ParameterRangeBool:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        size = larger.end_index() - smaller.start
        return ParameterRangeBool(
            name=self.name,
            type="bool",
            size=size,
            ambient_index=smaller.ambient_index,
            start=smaller.start,
            step=self.step,
        )


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

    def get_step(self) -> PrimitiveValueType:
        return self.step

    def merge(self, other: ParameterRangeInt) -> ParameterRangeInt:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        return ParameterRangeInt(
            name=self.name,
            type="int",
            size=self.size + other.size,
            ambient_index=smaller.ambient_index,
            start=smaller.start,
            step=self.step,
        )


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

    def get_step(self) -> PrimitiveValueType:
        return self.step

    def merge(self, other: LineSegment) -> LineSegment:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        return ParameterRangeFloat(
            name=self.name,
            type="float",
            size=self.size + other.size,
            ambient_index=smaller.ambient_index,
            start=smaller.start,
            step=self.step,
        )


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
        return all(s.derived_by_same_ambient_space_with(o) for s, o in zip(self.axes, other.axes, strict=True))

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

        if not all(self.axes[d] == other.axes[d] for d in range(target_dim)):
            # target_dim より浅層の各次元が一致していなければ False
            return False

        self_axis = self.axes[target_dim]
        other_axis = other.axes[target_dim]
        return self_axis.can_merge(other_axis)

    def merge(self, other: ParameterAlignedSpace, target_dim: int) -> ParameterAlignedSpace:
        axes = []
        filling = []
        for d in range(self.get_dim()):
            if d != target_dim:
                # 浅層次元か深層次元: 同じはずなのでそのままコピー
                axes.append(self.axes[d])
                filling.append(self.filling_dim[d])
                continue

            # target_dim
            merged_axis = self.axes[d].merge(other.axes[d])
            axes.append(merged_axis)
            filling.append(merged_axis.is_universal())

        return ParameterAlignedSpace(axes=axes, filling_dim=filling)


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
