from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, override

import aiofiles.os

from lite_dist2.common import async_read_file, async_write_file
from lite_dist2.curriculum_models.trial import TrialModel
from lite_dist2.trial_repositories.base_trial_repository import BaseTrialRepository
from lite_dist2.trial_repositories.trial_repository_model import TrialRepositoryModel

if TYPE_CHECKING:
    from pathlib import Path

    from lite_dist2.type_definitions import TrialRepositoryType


class NormalTrialRepository(BaseTrialRepository):
    def __init__(self, save_dir: Path) -> None:
        self.save_dir = save_dir

    @override
    @staticmethod
    def get_repository_type() -> TrialRepositoryType:
        return "normal"

    @override
    async def clean_save_dir(self) -> None:
        if self.save_dir.exists():
            for item in self.save_dir.iterdir():
                if item.is_file() or item.is_symlink():
                    await aiofiles.os.remove(item)
                else:
                    warnings.warn(f"Unexpected item in save_dir: {item}", stacklevel=2)
        else:
            await aiofiles.os.mkdir(self.save_dir)

    @override
    async def save(self, trial: TrialModel) -> None:
        path = self.save_dir / f"{trial.trial_id}.json"
        await async_write_file(path, trial.model_dump_json().encode("utf-8"))

    @override
    async def load(self, trial_id: str) -> TrialModel:
        path = self.save_dir / f"{trial_id}.json"
        content = await async_read_file(path)
        return TrialModel.model_validate_json(content)

    @override
    async def load_all(self) -> list[TrialModel]:
        trials = []
        if not self.save_dir.exists() or not self.save_dir.is_dir():
            raise FileNotFoundError(self.save_dir)

        for json_path in self.save_dir.glob("*.json"):
            content = await async_read_file(json_path)
            trials.append(TrialModel.model_validate_json(content))
        return trials

    @override
    async def delete_save_dir(self) -> None:
        # ディレクトリ内の全ファイルを削除
        if self.save_dir.exists() and self.save_dir.is_dir():
            for item in self.save_dir.iterdir():
                if item.is_file() or item.is_symlink():
                    await aiofiles.os.remove(item)
            # ディレクトリ自体を削除
            await aiofiles.os.rmdir(self.save_dir)

    @override
    def to_model(self) -> TrialRepositoryModel:
        return TrialRepositoryModel(type=self.get_repository_type(), save_dir=self.save_dir)

    @staticmethod
    def from_model(model: TrialRepositoryModel) -> NormalTrialRepository:
        return NormalTrialRepository(model.save_dir)
