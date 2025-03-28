from typing import Any

import pytest

from lite_dist2.value_models.point import ScalerValue


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
            ScalerValue(type="scaler", value_type="int", value=True, name="some int")
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
def test_scaler_vector_deserialize(json_dict: dict[str, Any], expected: ScalerValue) -> None:
    actual = ScalerValue.model_validate(json_dict)
    assert actual == expected