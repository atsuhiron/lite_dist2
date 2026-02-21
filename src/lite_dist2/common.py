from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Literal

import aiofiles

from lite_dist2.expections import LD2ModelTypeError

if TYPE_CHECKING:
    from pathlib import Path

    from lite_dist2.type_definitions import PortableValueType, PrimitiveValueType


def hex2int(hex_str: str) -> int:
    return int(hex_str, base=16)


def int2hex(val: int) -> str:
    return hex(val)


def hex2float(hex_str: str) -> float:
    return float.fromhex(hex_str)


def float2hex(val: float) -> str:
    return float(val).hex()


def numerize(type_name: Literal["bool", "int", "float"], value: PortableValueType) -> PrimitiveValueType:
    match type_name:
        case "bool":
            return bool(value)
        case "int":
            return hex2int(str(value))
        case "float":
            return hex2float(str(value))
        case _:
            raise LD2ModelTypeError(type_name)


def portablize(type_name: Literal["bool", "int", "float"], value: PrimitiveValueType) -> PortableValueType:
    match type_name:
        case "bool":
            return bool(value)
        case "int":
            return int2hex(int(value))
        case "float":
            return float2hex(value)
        case _:
            raise LD2ModelTypeError(type_name)


def publish_timestamp() -> datetime:
    return datetime.now(tz=timezone(timedelta(hours=+9), "JST"))


async def async_read_file(path: Path) -> bytes:
    async with aiofiles.open(path, mode="rb") as f:
        return await f.read()


async def async_write_file(path: Path, data: bytes) -> None:
    async with aiofiles.open(path, mode="wb") as f:
        await f.write(data)
