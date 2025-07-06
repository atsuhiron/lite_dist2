import abc
from pathlib import Path

from lite_dist2.curriculum_models.trial import Trial


class BaseTrialRepository(abc.ABC):
    def __init__(self, trial_file_dir: Path, study_id: str) -> None:
        self.save_dir = trial_file_dir / study_id

    @abc.abstractmethod
    def clean_save_dir(self) -> None:
        pass

    @abc.abstractmethod
    def save(self, trial: Trial) -> None:
        pass

    @abc.abstractmethod
    def load(self, trial_id: str) -> Trial:
        pass

    @abc.abstractmethod
    def load_all(self) -> list[Trial]:
        pass
