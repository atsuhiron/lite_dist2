from __future__ import annotations

import abc
import itertools
from typing import TYPE_CHECKING

from pydantic import BaseModel

from lite_dist2.expections import LD2ParameterError, LD2UndefinedError
from lite_dist2.type_definitions import PrimitiveValueType
from lite_dist2.value_models.line_segment import (
    DummyLineSegment,
    LineSegmentModel,
    ParameterRangeBool,
    ParameterRangeFloat,
    ParameterRangeInt,
)
from lite_dist2.value_models.point import ParamType, ScalerValue

if TYPE_CHECKING:
    from collections.abc import Generator


class ParameterAlignedSpaceModel(BaseModel):
    axes: list[LineSegmentModel]


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


class ParameterAlignedSpace(ParameterSpace):
    def __init__(self, axes: list[ParameterRangeBool | ParameterRangeInt | ParameterRangeFloat]) -> None:
        self.axes = axes  # larger index, deeper dimension
        self.filling_dim = [axis.is_universal() for axis in self.axes]

        self._dimensional_size = tuple(axis.size for axis in self.axes)
        self._dim = len(self._dimensional_size)
        self._total = 1
        for axis in self.axes:
            self._total *= axis.size

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParameterAlignedSpace):
            return self.axes == other.axes
        return False

    def get_dim(self) -> int:
        return self._dim

    def get_dimensional_size(self) -> tuple[int, ...]:
        return self._dimensional_size

    def get_total(self) -> int:
        return self._total

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from itertools.product(*(axis.grid() for axis in self.axes))

    def indexed_grid(self) -> Generator[tuple[tuple[int, PrimitiveValueType], ...], None, None]:
        yield from itertools.product(*(axis.indexed_grid() for axis in self.axes))

    def slice(self, start_and_sizes: list[tuple[int, int]]) -> ParameterAlignedSpace:
        if len(start_and_sizes) != self.get_dim():
            msg = "start_and_sizes"
            raise LD2ParameterError(msg, "different size to axes")

        axes = [self.axes[i].slice(*start_and_sizes[i]) for i in range(self.get_dim())]
        return ParameterAlignedSpace(axes=axes)

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
        for d in range(self.get_dim()):
            if d != target_dim:
                # 浅層次元か深層次元: 同じはずなのでそのままコピー
                axes.append(self.axes[d])
                continue

            # target_dim
            merged_axis = self.axes[d].merge(other.axes[d])
            axes.append(merged_axis)

        return ParameterAlignedSpace(axes=axes)

    def to_model(self) -> ParameterAlignedSpaceModel:
        return ParameterAlignedSpaceModel(axes=[axis.to_model() for axis in self.axes])

    @staticmethod
    def from_model(space_model: ParameterAlignedSpaceModel) -> ParameterAlignedSpace:
        axes = []
        for axis_model in space_model.axes:
            match axis_model.type:
                case "bool":
                    axis = ParameterRangeBool.from_model(axis_model)
                case "int":
                    axis = ParameterRangeInt.from_model(axis_model)
                case "float":
                    axis = ParameterRangeFloat.from_model(axis_model)
                case _:
                    raise LD2UndefinedError(axis_model.type)
            axes.append(axis)

        return ParameterAlignedSpace(axes=axes)


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
    pri1 = ParameterRangeInt(name="x", type="int", start=100, size=4, ambient_index=0)
    pri2 = ParameterRangeInt(name="y", type="int", start=100, size=6, ambient_index=0)
    space = ParameterAlignedSpace(axes=[pri1, pri2])
    for g in space.grid():
        print(g)  # noqa: T201
