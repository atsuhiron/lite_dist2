from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9), "JST")
DEFAULT_TIMEOUT_MINUTE = 10
CURRICULUM_PATH = "curriculum.json"


def hex2int(hex_str: str) -> int:
    return int(hex_str, base=16)


def int2hex(val: int) -> str:
    return hex(val)


def hex2float(hex_str: str) -> float:
    return float.fromhex(hex_str)


def float2hex(val: float) -> str:
    return val.hex()


def publish_timestamp() -> datetime:
    return datetime.now(tz=JST)
