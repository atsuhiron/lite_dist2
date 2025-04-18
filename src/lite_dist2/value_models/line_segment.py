from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field

from lite_dist2.common import float2hex, hex2float, hex2int, int2hex
from lite_dist2.expections import LD2InvalidSpaceError, LD2ParameterError
from lite_dist2.interfaces import Mergeable

if TYPE_CHECKING:
    from collections.abc import Generator

    from lite_dist2.type_definitions import PrimitiveValueType


class LineSegmentModel(BaseModel):
    name: str | None = None
    type: Literal["bool", "int", "float"]
    size: int
    step: int | str
    start: bool | str
    ambient_index: str
    ambient_size: str | None = None
    is_dummy: bool = False


class LineSegment(BaseModel, Mergeable, metaclass=abc.ABCMeta):
    name: str | None = None
    type: Literal["bool", "int", "float"]
    size: int | None
    ambient_index: int
    ambient_size: int | None = None

    @abc.abstractmethod
    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        pass

    @abc.abstractmethod
    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        pass

    @abc.abstractmethod
    def slice(self, start_index: int, size: int) -> LineSegment:
        pass

    @abc.abstractmethod
    def get_step(self) -> PrimitiveValueType:
        pass

    @abc.abstractmethod
    def merge(self, other: LineSegment, *args: object) -> LineSegment:
        pass

    def derived_by_same_ambient_space_with(self, other: LineSegment) -> bool:
        return (
            (self.name == other.name)
            and (self.type == other.type)
            and (self.get_step() == other.get_step())
            and (self.ambient_size == other.ambient_size)
        )

    def can_merge(self, other: LineSegment, *_: object) -> bool:
        if self.ambient_index < other.ambient_index:
            smaller = self
            larger = other
        else:
            smaller = other
            larger = self

        return smaller.end_index() + 1 >= larger.ambient_index

    def end_index(self) -> int:
        if self.size is None:
            msg = "Cannot get end index because this axis is infinite."
            raise LD2InvalidSpaceError(msg)
        return self.ambient_index + self.size - 1

    def is_universal(self) -> bool:
        if self.ambient_size is None:
            return False
        return self.size == self.ambient_size

    @abc.abstractmethod
    def to_model(self) -> LineSegmentModel:
        pass

    @staticmethod
    @abc.abstractmethod
    def from_model(line_segment_model: LineSegmentModel) -> LineSegment:
        pass


class DummyLineSegment(LineSegment):
    name: str
    type: Literal["bool", "int", "float"]
    size: Literal[1] = 1
    ambient_index: Literal[0] = 0
    ambient_size: Literal[1] = 1

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        yield from ()

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        yield from ()

    def slice(self, _start_index: int, _size: int) -> DummyLineSegment:
        return self

    def get_step(self) -> PrimitiveValueType:
        return 1

    def get_start_index(self, *_: object) -> int:
        return 0

    def can_merge(self, _other: LineSegment, *_: object) -> bool:
        return False

    def merge(self, _other: LineSegment, *_: object) -> LineSegment:
        return self

    def to_model(self) -> LineSegmentModel:
        return LineSegmentModel(
            name=self.name,
            type=self.type,
            size=self.size,
            step=self.get_step(),
            start="0x0",
            ambient_index="0x0",
            ambient_size="0x1",
            is_dummy=True,
        )

    @staticmethod
    def from_model(line_segment_model: LineSegmentModel) -> DummyLineSegment:
        return DummyLineSegment(
            name=line_segment_model.name,
            type=line_segment_model.type,
        )


class ParameterRangeBool(LineSegment):
    type: Literal["bool"]
    start: bool
    size: Annotated[int, Field(..., ge=1, le=2)]
    step: Annotated[int, Field(1, ge=1, le=1)]
    step: int = 1
    ambient_size: Annotated[int, Field(..., ge=1, le=2)]

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        for i in range(self.size):
            yield bool(int(self.start) + i)

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        for i in range(self.size):
            yield i, bool(int(self.start) + i)

    def slice(self, start_index: int, size: int) -> ParameterRangeBool:
        if size > self.size - start_index:
            msg = f"{size=}"
            raise LD2ParameterError(msg, "larger than ambient")
        return ParameterRangeBool(
            name=self.name,
            type="bool",
            start=bool(self.start + start_index * self.step),
            size=size,
            step=self.step,
            ambient_index=self.ambient_index + start_index,
            ambient_size=self.ambient_size,
        )

    def get_step(self) -> PrimitiveValueType:
        return self.step

    def get_start_index(self, *_: object) -> int:
        return self.ambient_index

    def merge(self, other: ParameterRangeBool, *_: object) -> ParameterRangeBool:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        size = larger.end_index() - smaller.start + 1
        return ParameterRangeBool(
            name=self.name,
            type="bool",
            size=size,
            ambient_index=smaller.ambient_index,
            ambient_size=self.ambient_size,
            start=smaller.start,
            step=self.step,
        )

    def to_model(self) -> LineSegmentModel:
        return LineSegmentModel(
            name=self.name,
            type=self.type,
            start=self.start,
            size=self.size,
            step=self.step,
            ambient_index=int2hex(self.ambient_index),
            ambient_size=int2hex(self.ambient_size),
        )

    @staticmethod
    def from_model(line_segment_model: LineSegmentModel) -> ParameterRangeBool:
        return ParameterRangeBool(
            name=line_segment_model.name,
            type="bool",
            size=line_segment_model.size,
            ambient_index=hex2int(line_segment_model.ambient_index),
            ambient_size=None if line_segment_model.ambient_size is None else hex2int(line_segment_model.ambient_size),
            start=line_segment_model.start,
            step=line_segment_model.step,
        )


class ParameterRangeInt(LineSegment):
    type: Literal["int"]
    start: int
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[int, Field(1, ge=1)]
    step: int = 1

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        for i in range(self.size):
            yield self.start + i * self.step

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        for i in range(self.size):
            yield i, self.start + i * self.step

    def slice(self, start_index: int, size: int) -> ParameterRangeInt:
        if size > self.size - start_index:
            msg = f"{size=}"
            raise LD2ParameterError(msg, "larger than ambient")
        return ParameterRangeInt(
            name=self.name,
            type="int",
            start=self.start + start_index * self.step,
            size=size,
            step=self.step,
            ambient_index=self.ambient_index + start_index,
            ambient_size=self.ambient_size,
        )

    def get_step(self) -> PrimitiveValueType:
        return self.step

    def get_start_index(self, *_: object) -> int:
        return self.ambient_index

    def merge(self, other: ParameterRangeInt, *_: object) -> ParameterRangeInt:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        size = larger.end_index() - smaller.start + 1
        return ParameterRangeInt(
            name=self.name,
            type="int",
            size=size,
            ambient_index=smaller.ambient_index,
            ambient_size=self.ambient_size,
            start=smaller.start,
            step=self.step,
        )

    def to_model(self) -> LineSegmentModel:
        return LineSegmentModel(
            name=self.name,
            type=self.type,
            start=int2hex(self.start),
            size=self.size,
            step=self.step,
            ambient_index=int2hex(self.ambient_index),
            ambient_size=int2hex(self.ambient_size),
        )

    @staticmethod
    def from_model(line_segment_model: LineSegmentModel) -> ParameterRangeInt:
        return ParameterRangeInt(
            name=line_segment_model.name,
            type="int",
            size=line_segment_model.size,
            ambient_index=hex2int(line_segment_model.ambient_index),
            ambient_size=None if line_segment_model.ambient_size is None else hex2int(line_segment_model.ambient_size),
            start=hex2int(line_segment_model.start),
            step=line_segment_model.step,
        )


class ParameterRangeFloat(LineSegment):
    type: Literal["float"]
    start: float
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[float, Field(..., gt=0)]

    def grid(self) -> Generator[PrimitiveValueType, None, None]:
        for i in range(self.size):
            yield self.start + i * self.step

    def indexed_grid(self) -> Generator[tuple[int, PrimitiveValueType], None, None]:
        for i in range(self.size):
            yield i, self.start + i * self.step

    def slice(self, start_index: int, size: int) -> ParameterRangeFloat:
        if size > self.size - start_index:
            msg = f"{size=}"
            raise LD2ParameterError(msg, "larger than ambient")
        return ParameterRangeFloat(
            name=self.name,
            type="float",
            start=self.start + start_index * self.step,
            size=size,
            step=self.step,
            ambient_index=self.ambient_index + start_index,
            ambient_size=self.ambient_size,
        )

    def get_step(self) -> PrimitiveValueType:
        return self.step

    def get_start_index(self, *_: object) -> int:
        return self.ambient_index

    def merge(self, other: LineSegment, *_: object) -> LineSegment:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        size = larger.end_index() - smaller.start + 1
        return ParameterRangeFloat(
            name=self.name,
            type="float",
            size=size,
            ambient_index=smaller.ambient_index,
            ambient_size=self.ambient_size,
            start=smaller.start,
            step=self.step,
        )

    def to_model(self) -> LineSegmentModel:
        return LineSegmentModel(
            name=self.name,
            type=self.type,
            start=float2hex(self.start),
            size=self.size,
            step=float2hex(self.step),
            ambient_index=int2hex(self.ambient_index),
            ambient_size=int2hex(self.ambient_size),
        )

    @staticmethod
    def from_model(line_segment_model: LineSegmentModel) -> ParameterRangeFloat:
        return ParameterRangeFloat(
            name=line_segment_model.name,
            type="float",
            size=line_segment_model.size,
            ambient_index=hex2int(line_segment_model.ambient_index),
            ambient_size=None if line_segment_model.ambient_size is None else hex2int(line_segment_model.ambient_size),
            start=hex2float(line_segment_model.start),
            step=hex2float(line_segment_model.step),
        )
