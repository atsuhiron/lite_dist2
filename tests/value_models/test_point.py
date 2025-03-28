from typing import Any

import pytest

from lite_dist2.value_models.point import ScalerValue, VectorValue


@pytest.mark.parametrize(
    ("json_dict", "expected"),
    [
        (
            {
                "type": "scaler",
                "value_type": "bool",
                "value": True,
                "name": "some flag"
            },
            ScalerValue(type="scaler", value_type="bool", value=True, name="some flag")
        ),
        (
            {
                "type": "scaler",
                "value_type": "int",
                "value": "f23",
                "name": "some int"
            },
            ScalerValue(type="scaler", value_type="int", value="f23", name="some int")
        ),
        (
            {
                "type": "scaler",
                "value_type": "float",
                "value": "0x1.999999999999ap-4",
                "name": "some float"
            },
            ScalerValue(type="scaler", value_type="float", value="0x1.999999999999ap-4", name="some float")
        )
    ]
)
def test_scaler_value_deserialize(json_dict: dict[str, Any], expected: ScalerValue) -> None:
    actual = ScalerValue.model_validate(json_dict)
    assert actual == expected


@pytest.mark.parametrize(
    ("scaler_value", "expected"),
    [
        (ScalerValue(type="scaler", value_type="bool", value=True), True),
        (ScalerValue(type="scaler", value_type="int", value="f23"), 3875),
        (ScalerValue(type="scaler", value_type="float", value="0x1.999999999999ap-4"), 0.1)
    ]
)
def test_scaler_value_numerize(scaler_value: ScalerValue, expected: bool | int | float):
    actual = scaler_value.numerize()
    assert actual == expected


@pytest.mark.parametrize(
    ("json_dict", "expected"),
    [
        (
            {
                "type": "vector",
                "value_type": "bool",
                "values": [True],
                "name": "some flag"
            },
            VectorValue(type="vector", value_type="bool", values=[True], name="some flag")
        ),
        (
            {
                "type": "vector",
                "value_type": "int",
                "values": ["f23"],
                "name": "some int"
            },
            VectorValue(type="vector", value_type="int", values=["f23"], name="some int")
        ),
        (
            {
                "type": "vector",
                "value_type": "float",
                "values": ["0x1.999999999999ap-4"],
                "name": "some float"
            },
            VectorValue(type="vector", value_type="float", values=["0x1.999999999999ap-4"], name="some float")
        )
    ]
)
def test_vector_value_deserialize(json_dict: dict[str, Any], expected: VectorValue) -> None:
    actual = VectorValue.model_validate(json_dict)
    assert actual == expected


@pytest.mark.parametrize(
    ("vector_value", "expected"),
    [
        (VectorValue(type="vector", value_type="bool", values=[True]), [True]),
        (VectorValue(type="vector", value_type="int", values=["f23"]), [3875]),
        (VectorValue(type="vector", value_type="float", values=["0x1.999999999999ap-4"]), [0.1])
    ]
)
def test_vector_value_numerize(vector_value: VectorValue, expected: list[bool | int | float]):
    actual = vector_value.numerize()
    assert actual == expected