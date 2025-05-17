from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class TableConfig(BaseModel):
    default_timeout_minutes: int = Field(
        default=10,
        description="Timeout minutes before a trial is reserved and registered",
    )
    curriculum_path: Path = Field(
        default=Path(__file__).parent.parent.parent / "curriculum.json",
        description="Path to the curriculum json file",
    )

    @staticmethod
    def load_from_file() -> TableConfig:
        path = Path(__file__).parent.parent.parent / "table_config.json"
        if not path.exists():
            msg = f"Table config file not found: {path}"
            raise FileNotFoundError(msg)
        with path.open() as f:
            return TableConfig.model_validate(json.load(f))


class WorkerConfig(BaseModel):
    @staticmethod
    def load_from_file() -> WorkerConfig:
        path = Path(__file__).parent.parent.parent / "worker_config.json"
        if not path.exists():
            msg = f"Worker config file not found: {path}"
            raise FileNotFoundError(msg)
        with path.open() as f:
            return WorkerConfig.model_validate(json.load(f))


class ConfigProvider:
    _TABLE: TableConfig | None = None
    _WORKER: WorkerConfig | None = None

    @classmethod
    def table(cls) -> TableConfig:
        if cls._TABLE is None:
            cls._TABLE = TableConfig.load_from_file()
        return cls._TABLE

    @classmethod
    def worker(cls) -> WorkerConfig:
        if cls._WORKER is None:
            cls._WORKER = WorkerConfig.load_from_file()
            return cls._WORKER
        return cls._WORKER
