from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Any

from lite_dist2.expections import LD2InvalidSpaceError, LD2ParameterError
from lite_dist2.suggest_strategies import BaseSuggestStrategy

if TYPE_CHECKING:
    from collections.abc import Generator

    from lite_dist2.study import TrialTable
    from lite_dist2.type_definitions import PrimitiveValueType
    from lite_dist2.value_models.space import (
        FlattenSegment,
        ParameterAlignedSpace,
        ParameterJaggedSpace,
        ParameterSpace,
    )


class SequentialSuggestStrategy(BaseSuggestStrategy):
    def __init__(
        self,
        suggest_parameter: dict[str, PrimitiveValueType | str],
        parameter_space: ParameterAlignedSpace,
    ) -> None:
        super().__init__(suggest_parameter, parameter_space)
        self.strict_aligned = self.suggest_parameter.get("strict_aligned", False)

    def suggest(self, trial_table: TrialTable, max_num: int) -> ParameterSpace:
        least_seg = trial_table.find_least_division(self.parameter_space.get_total)
        capped_max_num = self._nullable_min(least_seg.size, max_num)
        start = least_seg.start

        if self.strict_aligned:
            return self._aligned_suggest(start, capped_max_num)
        return self._jagged_suggest(capped_max_num)

    def _aligned_suggest(self, start: int, max_num: int) -> ParameterAlignedSpace:
        if self.parameter_space.is_infinite:
            available_end, infinite_flag = self._generate_available_end_infinite(start)
            if infinite_flag:
                max_available_gen = self._infinite_available_generator(
                    available_end,
                    self.parameter_space.lower_element_num_by_dim[0],
                )
                infinite_available_end = set()
                for _end_index in max_available_gen:
                    infinite_available_end.add(_end_index)
                    if _end_index - start > max_num:
                        break
                max_available_end = max(infinite_available_end)
            else:
                max_available_end: int = max(
                    filter(lambda end_index: end_index - start <= max_num, available_end),
                )

        else:
            available_end = self._generate_available_end_finite(start)
            max_available_end: int = max(
                filter(lambda end_index: end_index - start <= max_num, available_end),
            )

        start_loom = self.parameter_space.loom_by_flatten_index(
            start,
            self.parameter_space.lower_element_num_by_dim,
        )
        end_loom = self.parameter_space.loom_by_flatten_index(
            max_available_end,
            self.parameter_space.lower_element_num_by_dim,
        )
        start_and_sizes = [(s, e - s) for s, e in zip(start_loom, end_loom, strict=True)]
        return self.parameter_space.slice(start_and_sizes)

    def _jagged_suggest(self, max_num: int) -> ParameterJaggedSpace:
        parameters = []
        for i, param in enumerate(self.parameter_space.grid()):
            parameters.append(param)
            if i + 1 >= max_num:
                break
        return ParameterJaggedSpace(parameters, self.parameter_space.get_dummy_info)

    @staticmethod
    def _find_current_tick_index(least_seg: FlattenSegment, ticks: tuple[int, ...]) -> tuple[int, bool]:
        for i, tick in enumerate(ticks):
            if least_seg.start > tick:
                return i, False
            if least_seg.start == tick:
                return i, True
        return len(ticks) - 1, True  # all done

    @staticmethod
    def _nullable_min(a: int | None, b: int | None) -> int:
        if a is not None and b is not None:
            return min(a, b)
        if a is not None:
            return a
        if b is not None:
            return b
        target_param = "a, b"
        error_type = "both is None"
        raise LD2ParameterError(target_param, error_type)

    def _generate_available_end_finite(self, flatten_index: int) -> tuple[int, ...]:
        dims = self.parameter_space.get_dim
        reversed_dim_sizes = list(reversed(self.parameter_space.get_dimensional_sizes))
        lower_dims = self.parameter_space.lower_element_num_by_dim
        reversed_loomed_indices = list(reversed(self.parameter_space.loom_by_flatten_index(flatten_index, lower_dims)))

        total = self.parameter_space.get_total
        if self.parameter_space.is_infinite:
            msg = "Cannot use this method on infinite space"
            raise LD2InvalidSpaceError(msg)
        reversed_lower_dims = [*list(reversed(lower_dims)), total]

        available_max_upper_reverse_dim = 0  # larger, upper
        for dim, lower_dim in enumerate(lower_dims):
            if flatten_index % lower_dim == 0:
                available_max_upper_reverse_dim = dims - dim - 1
                break

        ticks = [flatten_index + 1]
        for reverse_dim in range(available_max_upper_reverse_dim + 1):
            lower_dim = reversed_lower_dims[reverse_dim]

            size = reversed_dim_sizes[reverse_dim] - reversed_loomed_indices[reverse_dim]
            if size <= 1:
                continue
            d_init = ticks[-1]
            for x in range(1, size):
                tick = d_init + lower_dim * x
                ticks.append(tick)
        return tuple(ticks)

    def _generate_available_end_infinite(self, flatten_index: int) -> tuple[tuple[int, ...], bool]:
        dims = self.parameter_space.get_dim
        reversed_dim_sizes = list(reversed(self.parameter_space.get_dimensional_sizes))
        lower_dims = self.parameter_space.lower_element_num_by_dim
        reversed_loomed_indices = list(reversed(self.parameter_space.loom_by_flatten_index(flatten_index, lower_dims)))

        if not self.parameter_space.is_infinite:
            msg = "Cannot use this method on finite space"
            raise LD2InvalidSpaceError(msg)

        reversed_lower_dims = list(reversed(lower_dims))

        available_max_upper_reverse_dim = 0  # larger, upper
        for dim, lower_dim in enumerate(lower_dims):
            if flatten_index % lower_dim == 0:
                available_max_upper_reverse_dim = dims - dim - 1
                break

        ticks = [flatten_index + 1]
        for reverse_dim in range(available_max_upper_reverse_dim + 1):
            lower_dim = reversed_lower_dims[reverse_dim]
            if reversed_dim_sizes[reverse_dim] is None:
                break

            size = reversed_dim_sizes[reverse_dim] - reversed_loomed_indices[reverse_dim]
            if size <= 1:
                continue
            d_init = ticks[-1]
            for x in range(1, size):
                tick = d_init + lower_dim * x
                ticks.append(tick)

        is_infinitely_available = ticks[-1] - flatten_index == lower_dims[0]
        return tuple(ticks), is_infinitely_available

    @staticmethod
    def _infinite_available_generator(init: tuple[int, ...], ratio: int) -> Generator[int, Any, None]:
        yield from init
        last_v = init[-1]
        for i in itertools.count(1):
            yield last_v + ratio * i
