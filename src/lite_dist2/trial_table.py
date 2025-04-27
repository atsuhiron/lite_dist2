from __future__ import annotations

import itertools

from pydantic import BaseModel

from lite_dist2.trial import Trial, TrialModel
from lite_dist2.value_models.parameter_aligned_space_helper import remap_space, simplify
from lite_dist2.value_models.space import FlattenSegment, ParameterAlignedSpace, ParameterAlignedSpaceModel


class TrialTableModel(BaseModel):
    trials: list[TrialModel]
    aggregated_parameter_space: dict[int, list[ParameterAlignedSpaceModel]] | None

    @staticmethod
    def create_empty() -> TrialTableModel:
        return TrialTableModel(trials=[], aggregated_parameter_space=None)


class TrialTable:
    def __init__(
        self,
        trials: list[Trial],
        aggregated_parameter_space: dict[int, list[ParameterAlignedSpace]] | None,
    ) -> None:
        self.trials = trials
        self.aggregated_parameter_space = aggregated_parameter_space

    def register(self, trial: Trial) -> None:
        self.trials.append(trial)

    def count_grid(self) -> int:
        if self.aggregated_parameter_space is None:
            return 0
        return sum(
            sum(space.get_total for space in spaces) for spaces in list(self.aggregated_parameter_space.values())
        )

    def count_trial(self) -> int:
        return len(self.trials)

    def simplify_aps(self) -> None:
        if not self._try_init_aps():
            return

        dim = self.trials[0].parameter_space.get_dim()
        remapped_spaces = []
        for d in reversed(range(dim)):
            simplified = simplify(self.aggregated_parameter_space[d], d)
            remapped_spaces.append(remap_space(simplified, dim))

        self.aggregated_parameter_space = {
            d: list(itertools.chain.from_iterable(remapped_space[d] for remapped_space in remapped_spaces))
            for d in range(-1, dim)
        }

    def find_least_division(self, total_num: int | None) -> FlattenSegment:
        if self.aggregated_parameter_space is None:
            return FlattenSegment(0, None)

        flatten_segments = [
            space.get_flatten_ambient_start_and_size()
            for spaces in self.aggregated_parameter_space.values()
            for space in spaces
        ]
        merged = simplify(flatten_segments)
        match len(merged):
            case 0:
                return FlattenSegment(0, None)
            case 1:
                start_index = merged[0].next_start_index()
                if total_num is None or start_index < total_num:
                    return FlattenSegment(start_index, None)
                return FlattenSegment(start_index, 0)
            case _:
                start = merged[0].next_start_index()
                return FlattenSegment(start, merged[1].get_start_index() - start)

    def _try_init_aps(self) -> bool:
        if self.aggregated_parameter_space is not None and len(self.aggregated_parameter_space) > 0:
            return True
        if len(self.trials) > 0:
            self.aggregated_parameter_space = {i: [] for i in range(-1, self.trials[0].parameter_space.get_dim())}
            return True
        return False

    def to_model(self) -> TrialTableModel:
        if self.aggregated_parameter_space is None:
            aps = None
        else:
            aps = {d: [space.to_model() for space in spaces] for d, spaces in self.aggregated_parameter_space.items()}
        return TrialTableModel(
            trials=[trial.to_model() for trial in self.trials],
            aggregated_parameter_space=aps,
        )

    @staticmethod
    def from_model(model: TrialTableModel) -> TrialTable:
        if model.aggregated_parameter_space is None:
            aps = None
        else:
            aps = {
                d: [ParameterAlignedSpace.from_model(space) for space in spaces]
                for d, spaces in model.aggregated_parameter_space.items()
            }
        return TrialTable(trials=[Trial.from_model(trial) for trial in model.trials], aggregated_parameter_space=aps)
