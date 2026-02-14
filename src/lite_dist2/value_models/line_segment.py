from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from lite_dist2.common import hex2float, hex2int, int2hex, portablize
from lite_dist2.expections import LD2InvalidSpaceError, LD2ParameterError
from lite_dist2.type_definitions import PortableValueType, PrimitiveValueType

if TYPE_CHECKING:
    from collections.abc import Generator


class LineSegment[T: PrimitiveValueType]:
    def __init__(
        self,
        name: str | None,
        type_: Literal["bool", "int", "float"],
        size: int | None,
        start: T,
        step: T,
        ambient_index: int,
        ambient_size: int | None,
        is_dummy: bool = False,
    ) -> None:
        self.name = name
        self.type = type_
        self.size = size
        self.start = start
        self.step = step
        self.ambient_index = ambient_index
        self.ambient_size = ambient_size
        self.is_dummy = is_dummy

        self._dtype = type(self.start)

    def __hash__(self) -> int:
        return hash((self.name, self.type, self.size, self.start, self.step, self.ambient_size, self.ambient_index))

    def grid(self) -> Generator[T]:
        fstart = float(self.start)
        fstep = float(self.step)
        i = 0
        while self.size is None or i < self.size:
            yield self._dtype(fstart + i * fstep)
            i += 1

    def indexed_grid(self) -> Generator[tuple[int, T], None, None]:
        i = 0
        while self.size is None or i < self.size:
            yield i + self.ambient_index, self.start + i * self.step
            i += 1

    def slice(self, start_index: int, size: int) -> LineSegment[T]:
        if self.size is not None and size > self.size - start_index:
            msg = f"{size=}"
            raise LD2ParameterError(msg, "larger than ambient")
        return LineSegment[T](
            name=self.name,
            type_=self.type,
            start=self._dtype(self.start + start_index * self.step),
            size=size,
            step=self.step,
            ambient_index=self.ambient_index + start_index,
            ambient_size=self.ambient_size,
        )

    def get_step(self) -> T:
        return self.step

    def get_start_index(self, *_: object) -> int:
        return self.ambient_index

    def merge(self, other: LineSegment, *_: object) -> LineSegment:
        smaller, larger = (self, other) if self.ambient_index < other.ambient_index else (other, self)
        size = larger.end_index() - smaller.ambient_index + 1
        return LineSegment[T](
            name=self.name,
            type_=self.type,
            size=size,
            ambient_index=smaller.ambient_index,
            ambient_size=self.ambient_size,
            start=smaller.start,
            step=self.step,
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

    def derived_by_same_ambient_space_with(self, other: LineSegment) -> bool:
        return (
            (self.name == other.name)
            and (self.type == other.type)
            and (self.get_step() == other.get_step())
            and (self.ambient_size == other.ambient_size)
        )

    def to_dummy(self) -> DummyLineSegmentModel:
        return DummyLineSegmentModel.from_line_segment(self)

    def to_model(self) -> LineSegmentModel:
        match self.start:
            # NOTE: self.start の型と T は一致しているので問題ない
            case bool():
                return ParameterRangeBoolModel.from_line_segment(self)  # ty: ignore[invalid-argument-type]
            case int():
                return ParameterRangeIntModel.from_line_segment(self)  # ty: ignore[invalid-argument-type]
            case float():
                return ParameterRangeFloatModel.from_line_segment(self)  # ty: ignore[invalid-argument-type]
            case _:
                msg = f"Invalid line segment type: {self.type}"
                raise LD2InvalidSpaceError(msg)


class _LineSegmentModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class DummyLineSegmentModel(_LineSegmentModel):
    type: Literal["bool", "int", "float"]
    name: str
    size: Literal[1] = 1
    step: PrimitiveValueType
    start: Literal[0] = 0
    ambient_index: Literal[0] = 0
    ambient_size: int | None
    is_dummy: Literal[True] = True

    def to_line_segment(self) -> LineSegment:
        return LineSegment(
            name=self.name,
            type_=self.type,
            size=self.size,
            start=self.start,
            step=self.step,
            ambient_index=self.ambient_index,
            ambient_size=self.ambient_size,
            is_dummy=self.is_dummy,
        )

    @staticmethod
    def from_line_segment(line_segment: LineSegment) -> DummyLineSegmentModel:
        return DummyLineSegmentModel(
            name=line_segment.name or "dummy",
            type=line_segment.type,
            step=line_segment.step,
            ambient_size=line_segment.ambient_size,
            is_dummy=True,
        )


class ParameterRangeBoolModel(_LineSegmentModel):
    type: Literal["bool"]
    name: str | None = None
    size: Annotated[int, Field(ge=1, le=2)]
    step: Annotated[int, Field(default=1, ge=1, le=1)] = 1
    start: bool
    ambient_index: Annotated[int, Field(ge=0, le=1)]
    ambient_size: Annotated[int, Field(ge=1, le=2)]
    is_dummy: Literal[False] = False

    def to_line_segment(self) -> LineSegment[bool]:
        return LineSegment[bool](
            name=self.name,
            type_=self.type,
            size=self.size,
            start=self.start,
            step=bool(self.step),
            ambient_index=self.ambient_index,
            ambient_size=self.ambient_size,
            is_dummy=self.is_dummy,
        )

    @staticmethod
    def from_line_segment(line_segment: LineSegment[bool]) -> ParameterRangeBoolModel:
        if line_segment.type != "bool":
            p = "type_"
            e = "'bool' is required"
            raise LD2ParameterError(p, e)
        if line_segment.size is None:
            p = "size"
            e = "size is required for bool type"
            raise LD2ParameterError(p, e)
        if line_segment.ambient_size is None:
            p = "ambient_size"
            e = "ambient_size is required for bool type"
            raise LD2ParameterError(p, e)
        if line_segment.is_dummy:
            p = "is_dummy"
            e = "is_dummy must be False for ParameterRangeBoolModel"
            raise LD2ParameterError(p, e)
        return ParameterRangeBoolModel(
            name=line_segment.name,
            type=line_segment.type,
            size=line_segment.size,
            start=bool(line_segment.start),
            step=int(line_segment.step),
            ambient_index=line_segment.ambient_index,
            ambient_size=line_segment.ambient_size,
            is_dummy=line_segment.is_dummy,
        )


class ParameterRangeIntModel(_LineSegmentModel):
    type: Literal["int"]
    name: str | None = None
    size: int | None
    step: Annotated[int, Field(default=1, ge=1)] = 1
    start: int
    ambient_index: Annotated[int, Field(ge=0)]
    ambient_size: Annotated[int | None, Field(ge=1)]
    is_dummy: Literal[False] = False

    def to_line_segment(self) -> LineSegment[int]:
        return LineSegment[int](
            name=self.name,
            type_=self.type,
            size=self.size,
            start=self.start,
            step=self.step,
            ambient_index=self.ambient_index,
            ambient_size=self.ambient_size,
            is_dummy=self.is_dummy,
        )

    @staticmethod
    def from_line_segment(line_segment: LineSegment[int]) -> ParameterRangeIntModel:
        if line_segment.type != "int":
            p = "type_"
            e = "'int' is required"
            raise LD2ParameterError(p, e)
        if line_segment.is_dummy:
            p = "is_dummy"
            e = "is_dummy must be False for ParameterRangeIntModel"
            raise LD2ParameterError(p, e)
        return ParameterRangeIntModel(
            name=line_segment.name,
            type=line_segment.type,
            size=line_segment.size,
            start=int(line_segment.start),
            step=int(line_segment.step),
            ambient_index=line_segment.ambient_index,
            ambient_size=line_segment.ambient_size,
            is_dummy=line_segment.is_dummy,
        )


class ParameterRangeFloatModel(_LineSegmentModel):
    type: Literal["float"]
    name: str | None = None
    size: int | None
    step: Annotated[float, Field(..., gt=0)]
    start: float
    ambient_index: Annotated[int, Field(ge=0)]
    ambient_size: Annotated[int | None, Field(ge=1)]
    is_dummy: Literal[False] = False

    def to_line_segment(self) -> LineSegment[float]:
        return LineSegment[float](
            name=self.name,
            type_=self.type,
            size=self.size,
            start=self.start,
            step=self.step,
            ambient_index=self.ambient_index,
            ambient_size=self.ambient_size,
            is_dummy=self.is_dummy,
        )

    @staticmethod
    def from_line_segment(line_segment: LineSegment[float]) -> ParameterRangeFloatModel:
        if line_segment.type != "float":
            p = "type_"
            e = "'float' is required"
            raise LD2ParameterError(p, e)
        if line_segment.is_dummy:
            p = "is_dummy"
            e = "is_dummy must be False for ParameterRangeFloatModel"
            raise LD2ParameterError(p, e)
        return ParameterRangeFloatModel(
            name=line_segment.name,
            type=line_segment.type,
            size=line_segment.size,
            start=float(line_segment.start),
            step=float(line_segment.step),
            ambient_index=line_segment.ambient_index,
            ambient_size=line_segment.ambient_size,
            is_dummy=line_segment.is_dummy,
        )


type StrictLineSegmentModel = ParameterRangeBoolModel | ParameterRangeIntModel | ParameterRangeFloatModel
type LineSegmentModel = StrictLineSegmentModel | DummyLineSegmentModel


class LineSegmentPortableModel(BaseModel):
    name: str | None = None
    type: Literal["bool", "int", "float"]
    size: str | None
    step: PortableValueType
    start: PortableValueType
    ambient_index: str
    ambient_size: str | None = None
    is_dummy: bool = False

    def to_line_segment_model(self) -> LineSegmentModel:
        if self.is_dummy:
            return DummyLineSegmentModel(
                name=self.name or "dummy",
                type=self.type,
                size=1,
                step=self.step if isinstance(self.step, bool) else hex2int(self.step),
                start=0,
                ambient_index=0,
                ambient_size=None if self.ambient_size is None else hex2int(self.ambient_size),
                is_dummy=True,
            )
        match self.type:
            case "bool":
                if self.size is None or self.ambient_size is None:
                    p = "size or ambient_size"
                    e = "size and ambient_size are required for bool type"
                    raise LD2ParameterError(p, e)
                return ParameterRangeBoolModel(
                    name=self.name,
                    type="bool",
                    size=hex2int(self.size),
                    step=int(self.step),
                    start=bool(self.start),
                    ambient_index=hex2int(self.ambient_index),
                    ambient_size=None if self.ambient_size is None else hex2int(self.ambient_size),
                    is_dummy=False,
                )
            case "int":
                return ParameterRangeIntModel(
                    name=self.name,
                    type=self.type,
                    size=None if self.size is None else hex2int(self.size),
                    start=hex2int(str(self.start)),
                    step=hex2int(str(self.step)),
                    ambient_index=hex2int(self.ambient_index),
                    ambient_size=None if self.ambient_size is None else hex2int(self.ambient_size),
                    is_dummy=False,
                )
            case "float":
                return ParameterRangeFloatModel(
                    name=self.name,
                    type=self.type,
                    size=None if self.size is None else hex2int(self.size),
                    start=hex2float(str(self.start)),
                    step=hex2float(str(self.step)),
                    ambient_index=hex2int(self.ambient_index),
                    ambient_size=None if self.ambient_size is None else hex2int(self.ambient_size),
                    is_dummy=False,
                )
            case _:
                msg = f"Invalid line segment type: {self.type}"
                raise LD2InvalidSpaceError(msg)

    @staticmethod
    def from_line_segment_model(line_segment_model: LineSegmentModel) -> LineSegmentPortableModel:
        return LineSegmentPortableModel(
            name=line_segment_model.name,
            type=line_segment_model.type,
            size=None if line_segment_model.size is None else int2hex(line_segment_model.size),
            start=portablize(line_segment_model.type, line_segment_model.start),
            step=portablize(line_segment_model.type, line_segment_model.step),
            ambient_index=int2hex(line_segment_model.ambient_index),
            ambient_size=None if line_segment_model.ambient_size is None else int2hex(line_segment_model.ambient_size),
            is_dummy=line_segment_model.is_dummy,
        )
