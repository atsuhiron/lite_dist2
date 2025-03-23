from typing import Iterable

from lite_dist2.value_models.point import ScalerValue, VectorValue

type PrimitiveValueType = int | float | bool
type RawParamType = tuple[PrimitiveValueType, ...]
type RawResultType = Iterable[PrimitiveValueType] | PrimitiveValueType
type ParamType = list[ScalerValue]
type ResultType = ScalerValue | VectorValue
