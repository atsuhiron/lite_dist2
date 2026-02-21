from __future__ import annotations

import abc
import itertools
from typing import TYPE_CHECKING

from lite_dist2.expections import LD2InvalidSpaceError

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from lite_dist2.type_definitions import PrimitiveValueType
    from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
    from lite_dist2.value_models.point import ParamType


class BaseSpace(abc.ABC):
    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abc.abstractmethod
    def __hash__(self) -> int:
        pass

    @abc.abstractmethod
    def dim(self) -> int:
        pass

    @abc.abstractmethod
    def total(self) -> int:
        pass

    @abc.abstractmethod
    def grid(self) -> Generator[tuple[PrimitiveValueType, ...]]:
        pass

    @abc.abstractmethod
    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        pass

    @abc.abstractmethod
    def to_aligned_list(self) -> list[ParameterAlignedSpace]:
        pass

    @abc.abstractmethod
    def lower_element_num_by_dim(self) -> tuple[int, ...]:
        pass

    @abc.abstractmethod
    def get_flatten_ambient_start_and_size_list(self) -> list[FlattenSegment]:
        pass

    @staticmethod
    def get_lower_element_num_by_dim(ambient_sizes: Sequence[int | None]) -> tuple[int, ...]:
        # ambient_sizes = (a, b, c, d) -> lower_element_num_by_dim = (bcd, cd, d, 1)
        inner_ambient_sizes = ambient_sizes[1:]
        if any(size is None for size in inner_ambient_sizes):
            msg = "Cannot contain inifinite dim in lower dim."
            raise LD2InvalidSpaceError(msg)

        return tuple(
            list(
                itertools.accumulate(
                    inner_ambient_sizes[::-1],
                    lambda x, y: x * y,
                    initial=1,
                ),
            )[::-1],
        )


class FlattenSegment:
    def __init__(self, start: int, size: int | None) -> None:
        self.start = start
        self.size = size

    def __repr__(self) -> str:
        return f"{FlattenSegment.__name__}(start={self.start}, size={self.size})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FlattenSegment):
            return (self.start == other.start) and (self.size == other.size)
        return False

    def __hash__(self) -> int:
        return hash((self.start, self.size))

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
        merged_size = None if smaller.size is None or larger.size is None else larger.start + larger.size
        return FlattenSegment(smaller.start, merged_size)

    def next_start_index(self) -> int:
        if self.size is None:
            msg = "Cannot get next start index because size of this segment is None"
            raise LD2InvalidSpaceError(msg)
        return self.start + self.size
