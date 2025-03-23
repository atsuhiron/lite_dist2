import abc
import itertools
from typing import Annotated, Generator, Literal

from pydantic import BaseModel, Field

from lite_dist2.common import hex2float, hex2int
from lite_dist2.type_definitions import ParamType, ValueType
from lite_dist2.value_models.point import Value


class LineSegment(BaseModel, metaclass=abc.ABCMeta):
    name: str | None = None

    @abc.abstractmethod
    def grid(self) -> Generator[ValueType, None, None]:
        pass


class ParameterRangeBool(LineSegment):
    type: Literal["bool"]
    start: bool
    size: Annotated[int, Field(..., ge=1, le=2)]
    step: Annotated[int, Field(1, ge=1, le=1)]

    def grid(self) -> Generator[ValueType, None, None]:
        for i in range(self.size):
            yield bool(int(self.start) + i)


class ParameterRangeInt(LineSegment):
    type: Literal["int"]
    start: str
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[int, Field(1, ge=1)]
    step: int = 1

    def grid(self) -> Generator[ValueType, None, None]:
        s = hex2int(self.start)
        for i in range(self.size):
            yield s + i * self.step


class ParameterRangeFloat(LineSegment):
    type: Literal["float"]
    start: str
    size: Annotated[int, Field(..., ge=1)]
    step: Annotated[float, Field(..., gt=0)]

    def grid(self) -> Generator[ValueType, None, None]:
        s = hex2float(self.start)
        for i in range(self.size):
            yield s + i * self.step


class ParameterSpace(BaseModel):
    axes: list[ParameterRangeBool | ParameterRangeInt | ParameterRangeFloat]

    def get_total(self) -> int:
        n = 1
        for axis in self.axes:
            n *= axis.size
        return n

    def grid(self) -> Generator[tuple[ValueType, ...], None, None]:
        for point in itertools.product(*(axis.grid() for axis in self.axes)):
            yield point

    def value_tuple_to_param_type(self, values: tuple[ValueType, ...]) -> ParamType:
        return [
            Value(type="scaler", value_type=ax.type, value=val, name=ax.name)
            for val, ax in zip(values, self.axes, strict=True)
        ]
