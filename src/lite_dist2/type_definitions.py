from collections.abc import Iterable

type PrimitiveValueType = int | float | bool
type PortableValueType = bool | str
type RawParamType = tuple[PrimitiveValueType, ...]
type RawResultType = Iterable[PrimitiveValueType] | PrimitiveValueType
type ConstParamType = int | float | bool | str
