from __future__ import annotations

import abc
import functools
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing.pool import Pool
from typing import TYPE_CHECKING, Any, override

import tqdm

from lite_dist2.expections import LD2TypeError
from lite_dist2.type_definitions import ConstParamType, PrimitiveValueType

if TYPE_CHECKING:
    from collections.abc import Iterator

    from lite_dist2.config import WorkerConfig
    from lite_dist2.curriculum_models.trial import Trial
    from lite_dist2.type_definitions import RawParamType, RawResultType
    from lite_dist2.value_models.space_type import ParameterSpaceType


logger = logging.getLogger(__name__)


class BaseTrialRunner(abc.ABC):
    @abc.abstractmethod
    def func(self, parameters: RawParamType, *args: object, **kwargs: object) -> RawResultType:
        pass

    @abc.abstractmethod
    def wrap_func(
        self,
        parameter_space: ParameterSpaceType,
        config: WorkerConfig,
        pool: Pool | ProcessPoolExecutor | None = None,
        *args: object,
        **kwargs: object,
    ) -> list[tuple[RawParamType, RawResultType]]:
        pass

    def parameter_pass_func(
        self,
        parameters: RawParamType,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[RawParamType, RawResultType]:
        return parameters, self.func(parameters, *args, **kwargs)

    def run(
        self,
        trial: Trial,
        config: WorkerConfig,
        pool: Pool | ProcessPoolExecutor | None = None,
        *args: object,
        **kwargs: object,
    ) -> Trial:
        raw_mappings = self.wrap_func(trial.parameter_space, config, pool, *args, **kwargs)
        mappings = trial.convert_mappings_from(raw_mappings)
        trial.set_result(mappings)
        return trial

    @staticmethod
    def get_typed[T](key: str, value_type: type[T], d: dict[str, object]) -> T:
        v = d.get(key)
        if isinstance(v, value_type):
            return v
        raise LD2TypeError(key, ConstParamType.__value__, type(v))


class AutoMPTrialRunner(BaseTrialRunner, abc.ABC):
    @override
    def wrap_func(
        self,
        parameter_space: ParameterSpaceType,
        config: WorkerConfig,
        pool: Pool | ProcessPoolExecutor | None = None,
        *args: object,
        **kwargs: object,
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        total = parameter_space.total
        tqdm_kwargs = {"total": total, "disable": config.disable_function_progress_bar}
        if config.process_num is None or config.process_num > 1:
            parameter_pass_func = functools.partial(self.parameter_pass_func, args=args, kwargs=kwargs)
            _pool = Pool(processes=config.process_num)
            try:
                with tqdm.tqdm(**tqdm_kwargs) as p_bar:
                    for arg_tuple, result_iter in _pool.imap_unordered(
                        func=parameter_pass_func,
                        iterable=parameter_space.grid(),
                        chunksize=config.chunk_size,
                    ):
                        raw_mappings.append((arg_tuple, result_iter))
                        p_bar.update(1)
                return raw_mappings
            except KeyboardInterrupt:
                _pool.terminate()
                _pool.join()
            else:
                _pool.close()
                _pool.join()
        return [
            self.parameter_pass_func(arg_tuple, args, kwargs)
            for arg_tuple in tqdm.tqdm(parameter_space.grid(), **tqdm_kwargs)
        ]


class SemiAutoMPTrialRunner(BaseTrialRunner, abc.ABC):
    @override
    def wrap_func(
        self,
        parameter_space: ParameterSpaceType,
        config: WorkerConfig,
        pool: Pool | ProcessPoolExecutor | None = None,
        *args: object,
        **kwargs: object,
    ) -> list[tuple[RawParamType, RawResultType]]:
        total = parameter_space.total
        tqdm_kwargs = {"total": total, "disable": config.disable_function_progress_bar}

        if pool is None:
            logger.warning("pool is None, running in single-threaded mode")
            return [
                self.parameter_pass_func(arg_tuple, args, kwargs)
                for arg_tuple in tqdm.tqdm(parameter_space.grid(), **tqdm_kwargs)
            ]

        parameter_pass_func = functools.partial(self.parameter_pass_func, args=args, kwargs=kwargs)
        grid = parameter_space.grid()
        match pool:
            case Pool():
                return self._run_pool(pool, parameter_pass_func, grid, config.chunk_size, tqdm_kwargs)
            case ProcessPoolExecutor():
                return self._run_process_pool_executor(pool, parameter_pass_func, grid, tqdm_kwargs)
            case _:
                n = "pool"
                raise LD2TypeError(n, "Pool or ProcessPoolExecutor", type(pool))

    def _run_pool(
        self,
        pool: Pool,
        parameter_pass_func: functools.partial[tuple[RawParamType, RawResultType]],
        grid: Iterator[tuple[PrimitiveValueType, ...]],
        chunk_size: int,
        tqdm_kwargs: dict[str, Any],
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        with tqdm.tqdm(**tqdm_kwargs) as p_bar:
            for arg_tuple, result_iter in pool.imap_unordered(
                func=parameter_pass_func,
                iterable=grid,
                chunksize=chunk_size,
            ):
                raw_mappings.append((arg_tuple, result_iter))
                p_bar.update(1)
        return raw_mappings

    def _run_process_pool_executor(
        self,
        pool: ProcessPoolExecutor,
        parameter_pass_func: functools.partial[tuple[RawParamType, RawResultType]],
        grid: Iterator[tuple[PrimitiveValueType, ...]],
        tqdm_kwargs: dict[str, Any],
    ) -> list[tuple[RawParamType, RawResultType]]:
        raw_mappings: list[tuple[RawParamType, RawResultType]] = []
        futures = {pool.submit(parameter_pass_func, arg_tuple): arg_tuple for arg_tuple in grid}
        with tqdm.tqdm(**tqdm_kwargs) as p_bar:
            for future in as_completed(futures):
                arg_tuple, result_iter = future.result()
                raw_mappings.append((arg_tuple, result_iter))
                p_bar.update(1)
        return raw_mappings


class ManualMPTrialRunner(BaseTrialRunner, abc.ABC):
    @override
    def func(self, parameters: RawParamType, *args: object, **kwargs: object) -> RawResultType:
        return 0

    @abc.abstractmethod
    def batch_func(
        self,
        raw_params: Iterator[RawParamType],
        config: WorkerConfig,
        *args: object,
        **kwargs: object,
    ) -> list[tuple[RawParamType, RawResultType]]:
        pass

    @override
    def wrap_func(
        self,
        parameter_space: ParameterSpaceType,
        config: WorkerConfig,
        pool: Pool | ProcessPoolExecutor | None = None,
        *args: object,
        **kwargs: object,
    ) -> list[tuple[RawParamType, RawResultType]]:
        return self.batch_func(parameter_space.grid(), config, *args, **kwargs)
