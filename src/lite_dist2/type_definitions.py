from collections.abc import Iterable

type PrimitiveValueType = int | float | bool
type RawParamType = tuple[PrimitiveValueType, ...]
type RawResultType = Iterable[PrimitiveValueType] | PrimitiveValueType
