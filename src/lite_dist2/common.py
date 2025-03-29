def hex2int(hex_str: str) -> int:
    return int("0x" + hex_str, base=16)


def int2hex(val: int) -> str:
    return hex(val)[2:]


def hex2float(hex_str: str) -> float:
    return float.fromhex(hex_str)


def float2hex(val: float) -> str:
    return val.hex()
