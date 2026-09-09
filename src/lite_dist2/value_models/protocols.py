from __future__ import annotations

from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class Mergeable(Protocol):
    def get_start_index(self, *args: object) -> int: ...
    def can_merge(self, other: Self, *args: object) -> bool: ...
    def merge(self, other: Self, *args: object) -> Self: ...
