from typing import Any, Literal

import pytest

from lite_dist2.expections import LD2ModelTypeError
from lite_dist2.value_models.point import ScalerValue, VectorValue


@pytest.mark.parametrize(
    ("json_dict", "expected"),
    [
        (
            {"type": "scaler", "value_type": "bool", "value": True, "name": "some flag"},
            ScalerValue(type="scaler", value_type="bool", value=True, name="some flag"),
        ),
        (
            {"type": "scaler", "value_type": "int", "value": "f23", "name": "some int"},
            ScalerValue(type="scaler", value_type="int", value="f23", name="some int"),
        ),
        (
            {"type": "scaler", "value_type": "float", "value": "0x1.999999999999ap-4", "name": "some float"},
            ScalerValue(type="scaler", value_type="float", value="0x1.999999999999ap-4", name="some float"),
        ),
    ],
)
def test_scaler_value_deserialize(json_dict: dict[str, Any], expected: ScalerValue) -> None:
    actual = ScalerValue.model_validate(json_dict)
    assert actual == expected


@pytest.mark.parametrize(
    ("scaler_value", "expected"),
    [
        (ScalerValue(type="scaler", value_type="bool", value=True), True),
        (ScalerValue(type="scaler", value_type="int", value="f23"), 3875),
        (ScalerValue(type="scaler", value_type="float", value="0x1.999999999999ap-4"), 0.1),
    ],
)
def test_scaler_value_numerize(scaler_value: ScalerValue, expected: bool | float) -> None:
    actual = scaler_value.numerize()
    assert actual == expected


def test_scaler_value_numerize_value_type_error() -> None:
    scaler = ScalerValue(type="scaler", value_type="bool", value=True)
    # noinspection PyTypeChecker
    scaler.value_type = "invalid"
    with pytest.raises(LD2ModelTypeError, match=r"Unknown\stype:\s"):
        _ = scaler.numerize()


@pytest.mark.parametrize(
    ("raw_result_value", "value_type", "name", "expected"),
    [
        (True, "bool", "flag", ScalerValue(type="scaler", value_type="bool", value=True, name="flag")),
        (3875, "int", "num", ScalerValue(type="scaler", value_type="int", value="f23", name="num")),
        (0.1, "float", None, ScalerValue(type="scaler", value_type="float", value="0x1.999999999999ap-4")),
    ],
)
def test_scaler_value_create_from_numeric(
    raw_result_value: bool | float,
    value_type: Literal["bool", "int", "float"],
    name: str | None,
    expected: ScalerValue,
) -> None:
    actual = ScalerValue.create_from_numeric(raw_result_value, value_type, name)
    assert actual == expected


def test_scaler_value_create_from_numeric_value_type_error() -> None:
    with pytest.raises(LD2ModelTypeError, match=r"Unknown\stype:\s"):
        # noinspection PyTypeChecker
        _ = ScalerValue.create_from_numeric(raw_result_value=True, value_type="invalid")


@pytest.mark.parametrize(
    ("json_dict", "expected"),
    [
        (
            {"type": "vector", "value_type": "bool", "values": [True], "name": "some flag"},
            VectorValue(type="vector", value_type="bool", values=[True], name="some flag"),
        ),
        (
            {"type": "vector", "value_type": "int", "values": ["f23"], "name": "some int"},
            VectorValue(type="vector", value_type="int", values=["f23"], name="some int"),
        ),
        (
            {"type": "vector", "value_type": "float", "values": ["0x1.999999999999ap-4"], "name": "some float"},
            VectorValue(type="vector", value_type="float", values=["0x1.999999999999ap-4"], name="some float"),
        ),
    ],
)
def test_vector_value_deserialize(json_dict: dict[str, Any], expected: VectorValue) -> None:
    actual = VectorValue.model_validate(json_dict)
    assert actual == expected


@pytest.mark.parametrize(
    ("vector_value", "expected"),
    [
        (VectorValue(type="vector", value_type="bool", values=[True]), [True]),
        (VectorValue(type="vector", value_type="int", values=["f23"]), [3875]),
        (VectorValue(type="vector", value_type="float", values=["0x1.999999999999ap-4"]), [0.1]),
    ],
)
def test_vector_value_numerize(vector_value: VectorValue, expected: list[bool | int | float]) -> None:
    actual = vector_value.numerize()
    assert actual == expected


def test_vector_value_numerize_value_type_error() -> None:
    vector = VectorValue(type="vector", value_type="bool", values=[True])
    # noinspection PyTypeChecker
    vector.value_type = "invalid"
    with pytest.raises(LD2ModelTypeError, match=r"Unknown\stype:\s"):
        _ = vector.numerize()


@pytest.mark.parametrize(
    ("raw_result_value", "value_type", "name", "expected"),
    [
        ([True], "bool", "flag", VectorValue(type="vector", value_type="bool", values=[True], name="flag")),
        ([3875], "int", "num", VectorValue(type="vector", value_type="int", values=["f23"], name="num")),
        ([0.1], "float", None, VectorValue(type="vector", value_type="float", values=["0x1.999999999999ap-4"])),
    ],
)
def test_vector_value_create_from_numeric(
    raw_result_value: list[bool | int | float],
    value_type: Literal["bool", "int", "float"],
    name: str | None,
    expected: VectorValue,
) -> None:
    actual = VectorValue.create_from_numeric(raw_result_value, value_type, name)
    assert actual == expected


def test_vector_value_create_from_numeric_value_type_error() -> None:
    with pytest.raises(LD2ModelTypeError, match=r"Unknown\stype:\s"):
        # noinspection PyTypeChecker
        _ = VectorValue.create_from_numeric(raw_result_value=[True], value_type="invalid")
