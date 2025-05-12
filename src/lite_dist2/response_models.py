from __future__ import annotations

from pydantic import BaseModel, Field

from lite_dist2.curriculum_models.study_portables import StudyStorage
from lite_dist2.curriculum_models.study_status import StudyStatus


class OkResponse(BaseModel):
    ok: bool = Field(...)


class StudyRegisteredResponse(BaseModel):
    study_id: str = Field(..., description="Published `study_id` of registered study.")


class StudyResponse(BaseModel):
    status: StudyStatus = Field(..., description="Status of the target Study.")
    result: StudyStorage | None = Field(
        None,
        description="Results of completed study. If the study is not completed or not found, then `None`.",
    )
