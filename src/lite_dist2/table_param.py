from __future__ import annotations

from pydantic import BaseModel, Field


class BaseParam(BaseModel):
    pass


class TrialReserveParam(BaseParam):
    retaining_capacity: set[str] = Field(
        ...,
        description="List of capabilities that the worker node has.",
    )
    max_size: int = Field(
        ...,
        description="The maximum size of parameter space reserving.",
    )
