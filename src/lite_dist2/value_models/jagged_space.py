from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from lite_dist2.common import hex2int, int2hex
from lite_dist2.expections import LD2ParameterError, LD2UndefinedError
from lite_dist2.type_definitions import PrimitiveValueType
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.base_space import ParameterSpace
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


class ParameterJaggedSpaceModel(BaseModel):
    type: Literal["jagged"]
    parameters: list[tuple[PrimitiveValueType, ...]]
    ambient_indices: list[tuple[str, ...]]
    axes_info: list[LineSegmentModel]


class ParameterJaggedSpace(ParameterSpace):
    def __init__(
        self,
        parameters: list[tuple[PrimitiveValueType, ...]],
        ambient_indices: list[tuple[int, ...]],
        axes_info: list[DummyLineSegment],
    ) -> None:
        self.parameters = parameters
        self.ambient_indices = ambient_indices
        self.axes_info = axes_info

    def __eq__(self, other: object) -> bool:
        # for cache and test
        if isinstance(other, ParameterJaggedSpace):
            return (self.parameters == other.parameters) and (self.axes_info == other.axes_info)
        return False

    def get_dim(self) -> int:
        return len(self.axes_info)

    def get_total(self) -> int:
        return len(self.parameters)

    def grid(self) -> Generator[tuple[PrimitiveValueType, ...], None, None]:
        yield from self.parameters

    def indexed_grid(self) -> Generator[tuple[tuple[int, PrimitiveValueType], ...], None, None]:
        raise NotImplementedError  # 到達しないはず??

    def value_tuple_to_param_type(self, values: tuple[PrimitiveValueType, ...]) -> ParamType:
        return tuple(
            [
                ScalerValue(type="scaler", value_type=ax.type, value=val, name=ax.name)
                for val, ax in zip(values, self.axes_info, strict=True)
            ],
        )

    def derived_by_same_ambient_space_with(self, other: ParameterSpace) -> bool:
        if isinstance(other, ParameterJaggedSpace):
            return self.axes_info == other.axes_info
        return False

    def to_aligned_list(self) -> list[ParameterAlignedSpace]:
        segment_types: list[type[LineSegment]] = []
        for dummy in self.axes_info:
            match dummy.type:
                case "bool":
                    segment_types.append(ParameterRangeBool)
                case "int":
                    segment_types.append(ParameterRangeInt)
                case "float":
                    segment_types.append(ParameterRangeFloat)
                case _:
                    raise LD2UndefinedError(dummy.type)

        space_by_line = defaultdict(list)
        for ambient_index, param in zip(self.ambient_indices, self.parameters, strict=True):
            space_by_line[ambient_index[1:]].append(
                ParameterAlignedSpace(
                    axes=[
                        lst(
                            type=axis_info.type,
                            name=axis_info.name,
                            start=p,
                            size=1,
                            step=axis_info.step,
                            ambient_index=amb_idx,
                            ambient_size=axis_info.ambient_size,
                        )
                        for lst, axis_info, p, amb_idx in zip(
                            segment_types,
                            self.axes_info,
                            param,
                            ambient_index,
                            strict=True,
                        )
                    ],
                    check_lower_filling=True,
                ),
            )
        spaces = []
        for v in space_by_line.values():
            spaces.extend(v)
        return spaces

    def to_model(self) -> ParameterJaggedSpaceModel:
        return ParameterJaggedSpaceModel(
            type="jagged",
            parameters=self.parameters,
            ambient_indices=[tuple(int2hex(idx) for idx in amb_idx) for amb_idx in self.ambient_indices],
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
            ambient_indices=[tuple(hex2int(idx) for idx in amb_idx) for amb_idx in model.ambient_indices],
            axes_info=axes_info,
        )
