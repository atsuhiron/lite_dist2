from __future__ import annotations

import abc
from multiprocessing.pool import Pool
from typing import TYPE_CHECKING

import tqdm

from lite_dist2.config import ConfigProvider

if TYPE_CHECKING:
    from collections.abc import Iterator

    from lite_dist2.curriculum_models.trial import Trial
    from lite_dist2.type_definitions import RawParamType, RawResultType
    from lite_dist2.value_models.base_space import ParameterSpace


class BaseTrialRunner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def func(self, *args: RawParamType) -> tuple[RawParamType, RawResultType]:
        pass

    @abc.abstractmethod
    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        pool: Pool | None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        pass

    def run(self, trial: Trial, pool: Pool | None = None) -> Trial:
        raw_mappings = self.wrap_func(trial.parameter_space, pool)
        mappings = trial.convert_mappings_from(raw_mappings)
        trial.set_result(mappings)
        return trial


class AutoMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        _: Pool | None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        total = parameter_space.get_total()
        config = ConfigProvider.worker()
        tqdm_kwargs = {"total": total, "disable": config.disable_function_progress_bar}
        if config.process_num is not None and config.process_num > 1:
            with Pool(processes=config.process_num) as pool, tqdm.tqdm(**tqdm_kwargs) as p_bar:
                for arg_tuple, result_iter in pool.imap_unordered(self.func, parameter_space.grid()):
                    raw_mappings.append((arg_tuple, result_iter))
                    p_bar.update(1)
            return raw_mappings
        return [self.func(arg_tuple) for arg_tuple in tqdm.tqdm(parameter_space.grid(), **tqdm_kwargs)]


class SemiAutoMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        pool: Pool | None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        total = parameter_space.get_total()
        config = ConfigProvider.worker()
        tqdm_kwargs = {"total": total, "disable": config.disable_function_progress_bar}
        if pool is not None:
            with tqdm.tqdm(**tqdm_kwargs) as p_bar:
                for arg_tuple, result_iter in pool.imap_unordered(self.func, parameter_space.grid()):
                    raw_mappings.append((arg_tuple, result_iter))
                    p_bar.update(1)
            return raw_mappings
        return [self.func(arg_tuple) for arg_tuple in tqdm.tqdm(parameter_space.grid(), **tqdm_kwargs)]


class ManualMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def func(self, *args: RawParamType) -> tuple[RawParamType, RawResultType]:
        pass

    @abc.abstractmethod
    def batch_func(self, raw_params: Iterator[RawParamType]) -> list[tuple[RawParamType, RawResultType]]:
        pass

    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        _pool: Pool | None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        return self.batch_func(parameter_space.grid())
