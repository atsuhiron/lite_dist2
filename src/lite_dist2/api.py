from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import Body, FastAPI, HTTPException
from fastapi.params import Query
from fastapi.responses import JSONResponse

from lite_dist2.curriculum_models.curriculum import CurriculumProvider, CurriculumSummaryModel
from lite_dist2.curriculum_models.study import Study, StudyStatus
from lite_dist2.response_models import OkResponse, StudyRegisteredResponse, StudyResponse

if TYPE_CHECKING:
    from lite_dist2.curriculum_models.study_portables import StudyRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/ping")
def handle_ping() -> OkResponse:
    return OkResponse(ok=True)


@app.get("/status", response_model=CurriculumSummaryModel)
def handle_status() -> CurriculumSummaryModel | JSONResponse:
    curr = CurriculumProvider.get()
    return JSONResponse(
        content=curr.to_summaries().model_dump(mode="json"),
        status_code=200,
    )


@app.post("/study/register", response_model=StudyRegisteredResponse)
def handle_study_register(
    study_registry: Annotated[StudyRegistry, Body(description="Registry of processing study")] = ...,
) -> StudyRegisteredResponse | JSONResponse:
    curr = CurriculumProvider.get()
    new_study = Study.from_model(study_registry.to_study_model())
    curr.insert_study(new_study)
    return JSONResponse(
        content=StudyRegisteredResponse(study_id=new_study.study_id).model_dump(mode="json"),
        status_code=200,
    )


@app.post("/trial/reserve")
def handle_trial_reserve() -> None:
    pass


@app.post("/trial/register")
def handle_trial_register() -> OkResponse:
    pass


@app.get("/study", response_model=StudyResponse)
def handle_study(
    study_id: Annotated[str | None, Query(description="`study_id` of the target study")] = None,
    name: Annotated[str | None, Query(description="`name` of the target study")] = None,
) -> StudyResponse | JSONResponse | HTTPException:
    if study_id is None and name is None:
        return HTTPException(status_code=400, detail="One of study_id or name should be set.")
    if study_id is not None and name is not None:
        return HTTPException(status_code=400, detail="Only one of study_id or name should be set.")

    curr = CurriculumProvider.get()
    storage = curr.pop_storage(study_id, name)
    if storage is not None:
        return JSONResponse(
            content=StudyResponse(status=StudyStatus.done, result=storage),
            status_code=200,
        )

    study_status = curr.get_study_status(study_id, name)
    resp = StudyResponse(status=study_status, result=None)
    if study_status == StudyStatus.not_found:
        return HTTPException(status_code=404, detail="Study not found")
    return JSONResponse(content=resp, status_code=202)
