from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from lite_dist2.type_definitions import PortableValueType
from lite_dist2.value_models.aligned_space import ParameterAlignedSpacePortableModel
from lite_dist2.value_models.line_segment import LineSegmentPortableModel


class LineSegmentRegistry(BaseModel):
    name: str | None = None
    type: Literal["bool", "int", "float"]
    size: str | None
    step: PortableValueType
    start: PortableValueType

    def to_line_segment_model(self) -> LineSegmentPortableModel:
        return LineSegmentPortableModel(
            name=self.name,
            type=self.type,
            size=self.size,
            step=self.step,
            start=self.start,
            ambient_index="0x0",
            ambient_size=self.size,
            is_dummy=False,
        )


class ParameterAlignedSpaceRegistry(BaseModel):
    type: Literal["aligned"]
    axes: list[LineSegmentRegistry]

    def to_parameter_aligned_space_model(self) -> ParameterAlignedSpacePortableModel:
        return ParameterAlignedSpacePortableModel(
            type=self.type,
            axes=[axis.to_line_segment_model() for axis in self.axes],
            check_lower_filling=True,
        )
