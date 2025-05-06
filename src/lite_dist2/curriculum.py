from __future__ import annotations

import threading

from pydantic import BaseModel

from lite_dist2.study import Study, StudyModel, StudyStatus


class CurriculumModel(BaseModel):
    studies: list[StudyModel]


class Curriculum:
    def __init__(self, studies: list[Study]) -> None:
        self.studies = studies
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

    def to_model(self) -> CurriculumModel:
        return CurriculumModel(
            studies=[study.to_model() for study in self.studies],
        )

    @staticmethod
    def from_model(model: CurriculumModel) -> Curriculum:
        return Curriculum(
            studies=[Study.from_model(study) for study in model.studies],
        )
