import abc

from lite_dist2.curriculum_models.trial import TrialModel
from lite_dist2.trial_repositories.trial_repository_model import TrialRepositoryModel
from lite_dist2.type_definitions import TrialRepositoryType


class BaseTrialRepository(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get_repository_type() -> TrialRepositoryType:
        pass

    @abc.abstractmethod
    async def clean_save_dir(self) -> None:
        pass

    @abc.abstractmethod
    async def save(self, trial: TrialModel) -> None:
        pass

    @abc.abstractmethod
    async def load(self, trial_id: str) -> TrialModel:
        pass

    @abc.abstractmethod
    async def load_all(self) -> list[TrialModel]:
        pass

    @abc.abstractmethod
    async def delete_save_dir(self) -> None:
        pass

    @abc.abstractmethod
    def to_model(self) -> TrialRepositoryModel:
        pass
