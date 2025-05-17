from __future__ import annotations

from pydantic import BaseModel, Field

from lite_dist2.curriculum_models.study_portables import StudyStorage, StudySummary
from lite_dist2.curriculum_models.study_status import StudyStatus
from lite_dist2.curriculum_models.trial import TrialModel


class OkResponse(BaseModel):
    ok: bool = Field(...)


class TrialReserveResponse(BaseModel):
    trial: TrialModel | None = Field(
        ...,
        description=(
            "Reserved trial for the worker node. "
            "None if the curriculum is empty or no trial which can be processed by the worker node's capabilities."
        ),
    )


class StudyRegisteredResponse(BaseModel):
    study_id: str = Field(
        ...,
        description="Published `study_id` of registered study.",
    )


class StudyResponse(BaseModel):
    status: StudyStatus = Field(
        ...,
        description="Status of the target Study.",
    )
    result: StudyStorage | None = Field(
        None,
        description="Results of completed study. If the study is not completed or not found, then `None`.",
    )


class CurriculumSummaryResponse(BaseModel):
    summaries: list[StudySummary] = Field(
        ...,
        description="The list of study (containing storage) summary.",
    )
