from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from lite_dist2.curriculum_models.trial import Mapping


class StudyStorage(BaseModel):
    study_id: str
    name: str | None
    registered_timestamp: datetime
    done_timestamp: datetime
    result_type: Literal["scaler", "vector"]
    result_value_type: Literal["bool", "int", "float"]
    result: list[Mapping]
