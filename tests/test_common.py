import pytest

from lite_dist2 import common


@pytest.mark.parametrize(
    ("hex_str", "expected"),
    [
        ("0", 0),
        ("01", 1),
        ("a", 10),
        ("a54f", 42319),
    ],
)
def test_hex2int(hex_str: str, expected: int) -> None:
    assert common.hex2int(hex_str) == expected


@pytest.mark.parametrize(
    ("int_val", "expected"),
    [
        (0, "0"),
        (10, "a"),
        (42319, "a54f"),
    ],
)
def test_int2hex(int_val: int, expected: str) -> None:
    assert common.int2hex(int_val) == expected


@pytest.mark.parametrize(
    ("hex_str", "expected"),
    [
        ("0x0.0p+0", 0.0),
        ("-0x0.0p+0", -0.0),
        ("0x1.999999999999ap-4", 0.1),
    ],
)
def test_hex2float(hex_str: str, expected: float) -> None:
    assert common.hex2float(hex_str) == expected


@pytest.mark.parametrize(
    ("float_val", "expected"),
    [
        (0.0, "0x0.0p+0"),
        (-0.0, "-0x0.0p+0"),
        (0.1, "0x1.999999999999ap-4"),
    ],
)
def test_float2hex(float_val: float, expected: str) -> None:
    assert common.float2hex(float_val) == expected
