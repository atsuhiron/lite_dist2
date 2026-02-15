from __future__ import annotations

import functools
from typing import Literal

from pydantic import BaseModel

from lite_dist2.common import hex2int
from lite_dist2.type_definitions import PortableValueType
from lite_dist2.value_models.line_segment import LineSegmentPortableModel


class ParameterAlignedSpacePortableModel(BaseModel):
    type: Literal["aligned"]
    axes: list[LineSegmentPortableModel]
    check_lower_filling: bool

    @functools.cached_property
    def total(self) -> int | None:
        t = 1
        for axis in self.axes:
            if axis.size is None:
                return None
            t *= hex2int(axis.size)
        return t


class ParameterJaggedSpacePortableModel(BaseModel):
    type: Literal["jagged"]
    parameters: list[tuple[PortableValueType, ...]]
    ambient_indices: list[tuple[str, ...]]
    axes_info: list[LineSegmentPortableModel]


type SpacePortableModelType = ParameterAlignedSpacePortableModel | ParameterJaggedSpacePortableModel
