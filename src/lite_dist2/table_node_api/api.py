from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Body, FastAPI, HTTPException, Query, Response, status

from lite_dist2.curriculum_models.curriculum import CurriculumProvider
from lite_dist2.curriculum_models.study import Study
from lite_dist2.curriculum_models.study_status import StudyStatus
from lite_dist2.curriculum_models.trial import Trial
from lite_dist2.expections import LD2ParameterError
from lite_dist2.table_node_api.table_param import StudyRegisterParam, TrialRegisterParam, TrialReserveParam
from lite_dist2.table_node_api.table_response import (
    CurriculumSummaryResponse,
    OkResponse,
    ProgressSummaryResponse,
    StudyRegisteredResponse,
    StudyResponse,
    TrialReserveResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    version="0.6.4",
)


@app.get("/ping")
def handle_ping() -> OkResponse:
    return OkResponse(ok=True)


@app.get("/save")
async def handle_save() -> OkResponse:
    curr = await CurriculumProvider.get()
    await curr.save()
    return OkResponse(ok=True)


@app.get("/status")
async def handle_status() -> CurriculumSummaryResponse:
    curr = await CurriculumProvider.get()
    return CurriculumSummaryResponse(summaries=curr.to_summaries())


@app.get("/status/progress")
async def handle_status_progress(
    cutoff_sec: Annotated[int, Query(description="Time range of Trial used for ETA estimation.")] = 600,
) -> ProgressSummaryResponse:
    curr = await CurriculumProvider.get()
    return curr.report_progress(cutoff_sec)


@app.post("/study/register")
async def handle_study_register(
    study_registry: Annotated[StudyRegisterParam, Body(description="Registry of processing study")],
) -> StudyRegisteredResponse:
    if not study_registry.study.is_valid():
        raise HTTPException(status_code=400, detail="Cannot use together infinite space and all_calculation strategy.")

    curr = await CurriculumProvider.get()
    new_study = Study.from_model(study_registry.study.to_study_model(curr.trial_file_dir))

    if curr.try_insert_study(new_study):
        await new_study.trial_repo.clean_save_dir()
        return StudyRegisteredResponse(study_id=new_study.study_id)
    raise HTTPException(status_code=400, detail=f'The name("{new_study.name}") of study is already registered.')


@app.post("/trial/reserve")
async def handle_trial_reserve(
    param: Annotated[TrialReserveParam, Body(description="Reserved trial parameter")],
    response: Response,
) -> TrialReserveResponse:
    curr = await CurriculumProvider.get()
    study = curr.get_available_study(param.retaining_capacity)
    if study is None:
        response.status_code = status.HTTP_202_ACCEPTED
        return TrialReserveResponse(trial=None)

    trial = study.suggest_next_trial(param.max_size, param.worker_node_name, param.worker_node_id)
    if trial is None:
        response.status_code = status.HTTP_202_ACCEPTED
        return TrialReserveResponse(trial=None)
    return TrialReserveResponse(trial=trial.to_model())


@app.post("/trial/register")
async def handle_trial_register(
    param: Annotated[TrialRegisterParam, Body(description="Registering trial")],
) -> OkResponse:
    curr = await CurriculumProvider.get()
    trial = param.trial
    study = curr.find_study_by_id(trial.study_id)
    if study is None:
        raise HTTPException(status_code=404, detail=f"Study not found: study_id={trial.study_id}")

    try:
        await study.receipt_trial(Trial.from_model(trial))
    except LD2ParameterError as e:
        raise HTTPException(
            status_code=409, detail="Invalid trial. Maybe the trial is not reserved or already registered."
        ) from e
    await curr.to_storage_if_done()
    return OkResponse(ok=True)


@app.get("/study")
async def handle_study(
    response: Response,
    study_id: Annotated[str | None, Query(description="`study_id` of the target study")] = None,
    name: Annotated[str | None, Query(description="`name` of the target study")] = None,
) -> StudyResponse:
    if study_id is None and name is None:
        raise HTTPException(status_code=400, detail="One of study_id or name should be set.")
    if study_id is not None and name is not None:
        raise HTTPException(status_code=400, detail="Only one of study_id or name should be set.")

    curr = await CurriculumProvider.get()
    storage = curr.get_storage(study_id, name)
    if storage is not None:
        await storage.consume_trial()
        return StudyResponse(status=StudyStatus.done, result=storage)

    # 見つからなかったか、終わってない
    study_status = curr.get_study_status(study_id, name)
    resp = StudyResponse(status=study_status, result=None)
    if study_status == StudyStatus.not_found:
        raise HTTPException(status_code=404, detail="Study not found.")

    response.status_code = status.HTTP_202_ACCEPTED
    return resp


@app.delete("/study")
async def handle_study_cancel(
    study_id: Annotated[str | None, Query(description="`study_id` of the target study")] = None,
    name: Annotated[str | None, Query(description="`name` of the target study")] = None,
) -> OkResponse:
    if study_id is None and name is None:
        raise HTTPException(status_code=400, detail="One of study_id or name should be set.")
    if study_id is not None and name is not None:
        raise HTTPException(status_code=400, detail="Only one of study_id or name should be set.")

    curr = await CurriculumProvider.get()
    try:
        found_and_cancel = await curr.cancel_study(study_id, name)
    except LD2ParameterError as e:
        raise HTTPException(status_code=400, detail="Invalid study_id or name.") from e

    if found_and_cancel:
        return OkResponse(ok=True)

    raise HTTPException(status_code=404, detail="Study not found.")
