from typing import Literal

from pydantic import BaseModel

from lite_dist2.common import hex2float, hex2int
from lite_dist2.expections import LD2InvalidParameterError
from lite_dist2.type_definitions import ValueType


class Value(BaseModel):
    type: Literal["scaler"]
    value_type: Literal["bool", "int", "float"]
    value: bool | str
    name: str | None = None

    def numerize(self) -> ValueType:
        match self.type:
            case "bool":
                return self.value
            case "int":
                return hex2int(self.value)
            case "float":
                return hex2float(self.value)
            case _:
                raise LD2InvalidParameterError(f"Unknown type: {self.type}")


class VectorValue(BaseModel):
    type: Literal["vector"]
    value_type: Literal["bool", "int", "float"]
    values: list[bool | str]
    name: str | None = None

    def numerize(self) -> list[ValueType]:
        match self.type:
            case "bool":
                return self.values
            case "int":
                return [hex2int(v) for v in self.values]
            case "float":
                return [hex2float(v) for v in self.values]
            case _:
                raise LD2InvalidParameterError(f"Unknown type: {self.type}")
