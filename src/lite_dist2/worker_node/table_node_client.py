from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests

from lite_dist2.curriculum_models.trial import Trial
from lite_dist2.expections import LD2TableNodeClientError, LD2TableNodeServerError
from lite_dist2.table_node_api.table_param import StudyRegisterParam, TrialRegisterParam, TrialReserveParam
from lite_dist2.table_node_api.table_response import StudyRegisteredResponse, TrialReserveResponse

if TYPE_CHECKING:
    from typing import Any, ClassVar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableNodeClient:
    INSTANT_API_TIMEOUT_SECONDS = 10
    HEADERS: ClassVar[dict[str, str]] = {"Content-Type": "application/json; charset=utf-8"}

    def __init__(self, ip: str, name: str) -> None:
        self.domain = "http://" + ip
        self.name = name  # TODO: これを登録できるようにする

    def ping(self) -> bool:
        try:
            _ = self._get("/ping", timeout=self.INSTANT_API_TIMEOUT_SECONDS)
        except LD2TableNodeServerError:
            return False
        return True

    # TODO: /study 用のメソッド作る

    def register_study(self, param: StudyRegisterParam) -> StudyRegisteredResponse:
        _, d = self._post("/study/register", self.INSTANT_API_TIMEOUT_SECONDS, param.model_dump(mode="json"))

        resp = StudyRegisteredResponse.model_validate(d)
        logger.info("Registered study: %s", resp.study_id)
        return resp

    def reserve_trial(self, max_size: int, retaining_capacity: set[str], timeout_seconds: int) -> Trial | None:
        param = TrialReserveParam(retaining_capacity=retaining_capacity, max_size=max_size)
        status_code, d = self._post("/trial/reserve", timeout_seconds, param.model_dump(mode="json"))

        resp = TrialReserveResponse.model_validate(d)
        if status_code == requests.codes.accepted or resp.trial is None:
            logger.info("Cannot reserve trial")
            return None

        trial = Trial.from_model(resp.trial)
        logger.info("Reserved trial (size=%d)", trial.parameter_space.get_total())
        return trial

    def register_trial(self, trial: Trial, timeout_seconds: int) -> None:
        param = TrialRegisterParam(trial=trial.to_model())
        _ = self._post("/trial/register", timeout_seconds, param.model_dump(mode="json"))

    def _get(self, path: str, timeout: int, query: dict[str, str] | None = None) -> tuple[int, dict[str, Any]]:
        url = f"{self.domain}{path}"
        response = requests.get(
            url,
            headers=self.HEADERS,
            params=query,
            timeout=timeout,
        )
        return response.status_code, self._check_status_code(response)

    def _post(self, path: str, timeout_seconds: int, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        url = f"{self.domain}{path}"
        response = requests.post(
            url,
            headers=self.HEADERS,
            json=body,
            timeout=timeout_seconds,
        )
        return response.status_code, self._check_status_code(response)

    @staticmethod
    def _check_status_code(response: requests.Response) -> dict[str, Any]:
        if response.status_code >= requests.codes.internal_server_error:
            raise LD2TableNodeServerError(response.text)
        if response.status_code >= requests.codes.bad_request:
            raise LD2TableNodeClientError(response.text)
        return response.json()
