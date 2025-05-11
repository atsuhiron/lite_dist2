from __future__ import annotations

import json
import logging
import pathlib
import threading
import time

from pydantic import BaseModel

from lite_dist2.common import CURRICULUM_PATH
from lite_dist2.curriculum_models.study import Study, StudyModel, StudyStatus
from lite_dist2.curriculum_models.study_storage import StudyStorage

logger = logging.getLogger(__name__)


class CurriculumModel(BaseModel):
    studies: list[StudyModel]
    storages: list[StudyStorage]


class Curriculum:
    def __init__(self, studies: list[Study], storages: list[StudyStorage]) -> None:
        self.studies = studies
        self.storages = storages
        self._lock = threading.Lock()

    def get_available_study(self, retaining_capacity: set[str]) -> Study | None:
        for study in self.studies:
            if study.status == StudyStatus.running and study.required_capacity.issubset(retaining_capacity):
                return study
        for study in self.studies:
            if study.status == StudyStatus.wait and study.required_capacity.issubset(retaining_capacity):
                return study
        return None

    def insert_study(self, study: Study) -> None:
        with self._lock:
            self.studies.append(study)

    def to_storage_if_done(self) -> None:
        with self._lock:
            self.studies = [study for study in self.studies if not self._move_to_storage_if_done(study)]

    def _move_to_storage_if_done(self, study: Study) -> bool:
        study.update_status()
        if study.is_done():
            self.storages.append(study.to_storage())
            return True
        return False

    def pop_storage(self, study_id: str | None, name: str | None) -> StudyStorage | None:
        storages = []
        target = None
        if study_id is not None:
            for storage in self.storages:
                if storage.study_id == study_id:
                    target = storage
                    continue
                storages.append(storage)
            self.storages = storages
            return target

        if name is not None:
            for storage in self.storages:
                if storage.name == name:
                    target = storage
                    continue
                storages.append(storage)
            self.storages = storages
            return target
        return None

    def get_study_status(self, study_id: str | None, name: str | None) -> StudyStatus:
        if study_id is not None:
            for study in self.studies:
                if study.study_id == study_id:
                    return study.status
        if name is not None:
            for study in self.studies:
                if study.name == name:
                    return study.status
        return StudyStatus.not_found

    def to_model(self) -> CurriculumModel:
        return CurriculumModel(
            studies=[study.to_model() for study in self.studies],
            storages=self.storages,
        )

    @staticmethod
    def from_model(model: CurriculumModel) -> Curriculum:
        return Curriculum(
            studies=[Study.from_model(study) for study in model.studies],
            storages=model.storages,
        )

    def save(self, curr_json_path: pathlib.Path | None = None) -> None:
        save_start_time = time.perf_counter()
        if curr_json_path is None:
            curr_json_path = pathlib.Path(__file__).parent.parent.parent / CURRICULUM_PATH

        model = self.to_model()
        with curr_json_path.open("w", encoding="utf-8") as f:
            json.dump(model.model_dump(mode="json"), f, ensure_ascii=False)
        save_end_time = time.perf_counter()
        logger.info("Saved curriculum in %.3f msec", (save_end_time - save_start_time) / 1000)

    @staticmethod
    def load_or_create(curr_json_path: pathlib.Path | None = None) -> Curriculum:
        load_start_time = time.perf_counter()
        if curr_json_path is None:
            curr_json_path = pathlib.Path(__file__).parent.parent.parent / CURRICULUM_PATH

        if curr_json_path.exists():
            with curr_json_path.open("r", encoding="utf-8") as f:
                json_dict = json.load(f)
            model = CurriculumModel.model_validate(json_dict)
            return Curriculum.from_model(model)
        load_end_time = time.perf_counter()
        logger.info("Loaded curriculum in %.3f msec", (load_end_time - load_start_time) / 1000)
        return Curriculum([], [])


class CurriculumProvider:
    _CURR = None

    @classmethod
    def get(cls) -> Curriculum:
        if cls._CURR is not None:
            return cls._CURR
        cls._CURR = Curriculum.load_or_create()
        return cls._CURR
