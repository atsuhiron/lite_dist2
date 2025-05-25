from __future__ import annotations

import abc
from multiprocessing.pool import Pool
from typing import TYPE_CHECKING

import tqdm

if TYPE_CHECKING:
    from collections.abc import Iterator

    from lite_dist2.config import WorkerConfig
    from lite_dist2.curriculum_models.trial import Trial
    from lite_dist2.type_definitions import RawParamType, RawResultType
    from lite_dist2.value_models.base_space import ParameterSpace


class BaseTrialRunner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def func(self, parameters: RawParamType) -> RawResultType:
        pass

    @abc.abstractmethod
    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        config: WorkerConfig,
        pool: Pool | None = None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        pass

    def parameter_pass_func(self, parameters: RawParamType) -> tuple[RawParamType, RawResultType]:
        return parameters, self.func(parameters)

    def run(self, trial: Trial, config: WorkerConfig, pool: Pool | None = None) -> Trial:
        raw_mappings = self.wrap_func(trial.parameter_space, config, pool)
        mappings = trial.convert_mappings_from(raw_mappings)
        trial.set_result(mappings)
        return trial


class AutoMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        config: WorkerConfig,
        _: Pool | None = None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        total = parameter_space.get_total()
        tqdm_kwargs = {"total": total, "disable": config.disable_function_progress_bar}
        if config.process_num is None or config.process_num > 1:
            with Pool(processes=config.process_num) as pool, tqdm.tqdm(**tqdm_kwargs) as p_bar:
                for arg_tuple, result_iter in pool.imap_unordered(self.parameter_pass_func, parameter_space.grid()):
                    raw_mappings.append((arg_tuple, result_iter))
                    p_bar.update(1)
            return raw_mappings
        return [self.parameter_pass_func(arg_tuple) for arg_tuple in tqdm.tqdm(parameter_space.grid(), **tqdm_kwargs)]


class SemiAutoMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        config: WorkerConfig,
        pool: Pool | None = None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        total = parameter_space.get_total()
        tqdm_kwargs = {"total": total, "disable": config.disable_function_progress_bar}
        if pool is not None:
            with tqdm.tqdm(**tqdm_kwargs) as p_bar:
                for arg_tuple, result_iter in pool.imap_unordered(self.parameter_pass_func, parameter_space.grid()):
                    raw_mappings.append((arg_tuple, result_iter))
                    p_bar.update(1)
            return raw_mappings
        return [self.parameter_pass_func(arg_tuple) for arg_tuple in tqdm.tqdm(parameter_space.grid(), **tqdm_kwargs)]


class ManualMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def func(self, *parameters: RawParamType) -> tuple[RawParamType, RawResultType]:
        pass

    @abc.abstractmethod
    def batch_func(self, raw_params: Iterator[RawParamType]) -> list[tuple[RawParamType, RawResultType]]:
        pass

    def wrap_func(
        self,
        parameter_space: ParameterSpace,
        _config: WorkerConfig,
        _: Pool | None = None,
    ) -> list[tuple[RawParamType, RawResultType]]:
        return self.batch_func(parameter_space.grid())
