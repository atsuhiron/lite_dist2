from __future__ import annotations

import abc
import itertools
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from lite_dist2.expections import LD2InvalidSpaceError, LD2ParameterError, LD2TypeError, LD2UndefinedError
from lite_dist2.interfaces import Mergeable
from lite_dist2.type_definitions import PrimitiveValueType
from lite_dist2.value_models.line_segment import (
    DummyLineSegment,
    LineSegment,
    LineSegmentModel,
    ParameterRangeBool,
    ParameterRangeFloat,
    ParameterRangeInt,
)
from lite_dist2.value_models.point import ParamType, ScalerValue

if TYPE_CHECKING:
    from collections.abc import Generator


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

    @abc.abstractmethod
    def to_model(self) -> ParameterAlignedSpaceModel | ParameterJaggedSpaceModel:
        pass


class FlattenSegment(Mergeable):
    def __init__(self, start: int, size: int | None) -> None:
        self.start = start
        self.size = size

    def __eq__(self, other: FlattenSegment) -> bool:
        if isinstance(other, FlattenSegment):
            return (self.start == other.start) and (self.size == other.size)
        return False

    def get_start_index(self, *_: object) -> int:
        return self.start

    def can_merge(self, other: FlattenSegment, *_: object) -> bool:
        if self.start < other.start:
            smaller = self
            larger = other
        else:
            smaller = other
            larger = self

        if smaller.size is None:
            return False

        return smaller.start + smaller.size >= larger.start

    def merge(self, other: FlattenSegment, *_: object) -> FlattenSegment:
        if self.start < other.start:
            smaller = self
            larger = other
        else:
            smaller = other
            larger = self
        return FlattenSegment(smaller.start, smaller.size + larger.start)

    def next_start_index(self) -> int:
        if self.size is None:
            msg = "Cannot get next start index because size of this segment is None"
            raise LD2InvalidSpaceError(msg)
        return self.start + self.size


class ParameterAlignedSpaceModel(BaseModel):
    type: Literal["aligned"]
    axes: list[LineSegmentModel]
    check_lower_filling: bool


class ParameterAlignedSpace(ParameterSpace, Mergeable):
    def __init__(self, axes: list[LineSegment], check_lower_filling: bool) -> None:
        self.axes = axes  # larger index, deeper dimension
        self.filling_dim = [axis.is_universal() for axis in self.axes]
        self.check_lower_filling = check_lower_filling

        self._dimensional_size = tuple(axis.size for axis in self.axes)
        self._dim = len(self._dimensional_size)
        self._total = self._calc_total()

        if self.check_lower_filling:
            self._check_lower_filling()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParameterAlignedSpace):
            return self.axes == other.axes
        return False

    def _check_lower_filling(self) -> None:
        #  F  F  F  T  T
        #  1  1  3  10 10
        #  i  f  f  f  f
        # のような場合のみ許可する
        for axis in self.axes[1:]:
            if axis.ambient_size is None:
                msg = "Infinite dimension is only allowed at the first dimension"
                raise LD2InvalidSpaceError(msg)

        is_lower_filled = False
        min_filled_dim = -1
        for i, fill in enumerate(self.filling_dim):
            if not is_lower_filled and fill:
                min_filled_dim = i
                is_lower_filled = True
                continue
            if is_lower_filled and (not fill):
                msg = "Filling from lower dimension"
                raise LD2InvalidSpaceError(msg)

        dim = self.get_dim()
        for i, axis in enumerate(self.axes):
            if i == dim - 1:
                continue
            if min_filled_dim == -1 and axis.size != 1:
                # No axis is universal
                msg = "Upper dimension must be size=1"
                raise LD2InvalidSpaceError(msg)
            if i < min_filled_dim - 1 and axis.size != 1:
                msg = "Upper dimension must be size=1"
                raise LD2InvalidSpaceError(msg)

    def _calc_total(self) -> int | None:
        t = 1
        for axis in self.axes:
            if axis.size is None:
                return None
            t *= axis.size
        return t

    def get_dim(self) -> int:
        return self._dim

    def get_dimensional_size(self) -> tuple[int, ...]:
        return self._dimensional_size

    def get_total(self) -> int | None:
        return self._total

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from itertools.product(*(axis.grid() for axis in self.axes))

    def get_flatten_ambient_start_and_size(self) -> FlattenSegment:
        if not self.check_lower_filling:
            msg = "Cannot get flatten info. Because check_lower_filling of this space is False."
            raise LD2InvalidSpaceError(msg)

        # ambient_sizes = (a, b, c, d) -> lower_element_num_by_dim = (bcd, cd, d, 1)
        lower_element_num_by_dim = list(
            itertools.accumulate([axis.ambient_size for axis in self.axes][1:][::-1], lambda x, y: x * y, initial=1),
        )[::-1]
        flatten_index = 0
        for di in range(self.get_dim()):
            flatten_index += self.axes[di].ambient_index * lower_element_num_by_dim[di]
        return FlattenSegment(flatten_index, self.get_total())

    def get_lower_not_universal_dim(self) -> int:
        for i in reversed(range(self._dim)):
            if not self.axes[i].is_universal():
                return i
        return -1

    def indexed_grid(self) -> Generator[tuple[tuple[int, PrimitiveValueType], ...], None, None]:
        yield from itertools.product(*(axis.indexed_grid() for axis in self.axes))

    def slice(self, start_and_sizes: list[tuple[int, int]]) -> ParameterAlignedSpace:
        if len(start_and_sizes) != self.get_dim():
            msg = "start_and_sizes"
            raise LD2ParameterError(msg, "different size to axes")

        axes = [self.axes[i].slice(*start_and_sizes[i]) for i in range(self.get_dim())]
        return ParameterAlignedSpace(axes=axes, check_lower_filling=self.check_lower_filling)

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

    def get_start_index(self, *args: object) -> int:
        if len(args) < 1:
            name = "target_dim"
            raise LD2ParameterError(name, "missing")

        target_dim = args[0]
        if not isinstance(target_dim, int):
            name = "target_dim"
            raise LD2TypeError(name, int, type(args[0]))
        return self.axes[target_dim].get_start_index()

    def can_merge(self, other: ParameterAlignedSpace, *args: object) -> bool:
        if len(args) < 1:
            name = "target_dim"
            raise LD2ParameterError(name, "missing")

        target_dim = args[0]
        if not isinstance(target_dim, int):
            name = "target_dim"
            raise LD2TypeError(name, int, type(args[0]))

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

    def merge(self, other: ParameterAlignedSpace, *args: object) -> ParameterAlignedSpace:
        if len(args) < 1:
            name = "target_dim"
            raise LD2ParameterError(name, "missing")

        target_dim = args[0]
        if not isinstance(target_dim, int):
            name = "target_dim"
            raise LD2TypeError(name, int, type(args[0]))

        axes = []
        for d in range(self.get_dim()):
            if d != target_dim:
                # 浅層次元か深層次元: 同じはずなのでそのままコピー
                axes.append(self.axes[d])
                continue

            # target_dim
            merged_axis = self.axes[d].merge(other.axes[d])
            axes.append(merged_axis)

        return ParameterAlignedSpace(axes=axes, check_lower_filling=self.check_lower_filling)

    def to_model(self) -> ParameterAlignedSpaceModel:
        return ParameterAlignedSpaceModel(
            type="aligned",
            axes=[axis.to_model() for axis in self.axes],
            check_lower_filling=self.check_lower_filling,
        )

    @staticmethod
    def from_model(space_model: ParameterAlignedSpaceModel) -> ParameterAlignedSpace:
        axes = []
        for axis_model in space_model.axes:
            if axis_model.is_dummy:
                param = f"{LineSegmentModel.__name__}.type"
                msg = f"An axis of {ParameterAlignedSpace.__name__} is not allowed dummy axis."
                raise LD2ParameterError(param, msg)

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

        return ParameterAlignedSpace(axes=axes, check_lower_filling=space_model.check_lower_filling)


class ParameterJaggedSpaceModel(BaseModel):
    type: Literal["jagged"]
    parameters: list[tuple[PrimitiveValueType, ...]]
    axes_info: list[LineSegmentModel]


class ParameterJaggedSpace(ParameterSpace):
    def __init__(self, parameters: list[tuple[PrimitiveValueType, ...]], axes_info: list[DummyLineSegment]) -> None:
        self.parameters = parameters
        self.axes_info = axes_info

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

    def to_model(self) -> ParameterJaggedSpaceModel:
        return ParameterJaggedSpaceModel(
            type="jagged",
            parameters=self.parameters,
            axes_info=[axis.to_model() for axis in self.axes_info],
        )

    @staticmethod
    def from_model(model: ParameterJaggedSpaceModel) -> ParameterJaggedSpace:
        axes_info = []
        for axis in model.axes_info:
            if not axis.is_dummy:
                param = f"{LineSegmentModel.__name__}.type"
                msg = f"An axis of {ParameterJaggedSpace.__name__} is only allowed dummy axis."
                raise LD2ParameterError(param, msg)
            axes_info.append(DummyLineSegment.from_model(axis))

        return ParameterJaggedSpace(
            parameters=model.parameters,
            axes_info=axes_info,
        )


if __name__ == "__main__":
    pri1 = ParameterRangeInt(name="x", type="int", start=100, size=4, ambient_index=0)
    pri2 = ParameterRangeInt(name="y", type="int", start=100, size=6, ambient_index=0)
    space = ParameterAlignedSpace(axes=[pri1, pri2], check_lower_filling=False)
    for g in space.grid():
        print(g)  # noqa: T201
