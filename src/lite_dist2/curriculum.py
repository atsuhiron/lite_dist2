from __future__ import annotations

import threading

from pydantic import BaseModel

from lite_dist2.study import Study, StudyModel, StudyStatus
from lite_dist2.study_storage import StudyStorage


class CurriculumModel(BaseModel):
    studies: list[StudyModel]
    storages: list[StudyStorage]


class Curriculum:
    def __init__(self, studies: list[Study], storages: list[StudyStorage]) -> None:
        self.studies = studies
        self.storages = storages
        self._lock = threading.Lock()

    def get_current_study(self) -> Study | None:
        for study in self.studies:
            if study.status == StudyStatus.running:
                return study
        for study in self.studies:
            if study.status == StudyStatus.reserved:
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
