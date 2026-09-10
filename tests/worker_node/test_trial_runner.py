from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool

import pytest

from lite_dist2.config import WorkerConfig
from lite_dist2.type_definitions import RawParamType, RawResultType
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import LineSegment
from lite_dist2.worker_node.trial_runner import AutoMPTrialRunner, SemiAutoMPTrialRunner


# Defined at module top level so that the runner instance stays picklable.
# Required by the "spawn" (Windows) and "forkserver" (Linux, default since Python 3.14) start methods.
class _Doubler(AutoMPTrialRunner):
    def func(self, parameters: RawParamType, *_args: object, **kwargs: object) -> RawResultType:
        offset = self.get_typed("offset", int, kwargs)
        return int(parameters[0]) * 2 + offset


class _SemiAutoDoubler(SemiAutoMPTrialRunner):
    def func(self, parameters: RawParamType, *_args: object, **kwargs: object) -> RawResultType:
        offset = self.get_typed("offset", int, kwargs)
        return int(parameters[0]) * 2 + offset


def _space(size: int) -> ParameterAlignedSpace:
    return ParameterAlignedSpace(
        axes=[LineSegment(name="x", type_="int", size=size, step=1, start=0, ambient_index=0, ambient_size=size)],
        check_lower_filling=True,
    )


_EXPECTED = [((0,), 10), ((1,), 12), ((2,), 14), ((3,), 16)]


@pytest.mark.parametrize("process_num", [1, 2])
def test_auto_mp_trial_runner_wrap_func(process_num: int) -> None:
    config = WorkerConfig(process_num=process_num, disable_function_progress_bar=True)
    actual = _Doubler().wrap_func(_space(4), config, None, offset=10)
    assert sorted(actual) == _EXPECTED


def test_semi_auto_mp_trial_runner_without_pool() -> None:
    config = WorkerConfig(disable_function_progress_bar=True)
    actual = _SemiAutoDoubler().wrap_func(_space(4), config, None, offset=10)
    assert sorted(actual) == _EXPECTED


def test_semi_auto_mp_trial_runner_with_process_pool_executor() -> None:
    config = WorkerConfig(disable_function_progress_bar=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        actual = _SemiAutoDoubler().wrap_func(_space(4), config, pool, offset=10)
    assert sorted(actual) == _EXPECTED


def test_semi_auto_mp_trial_runner_with_pool() -> None:
    config = WorkerConfig(disable_function_progress_bar=True)
    with Pool(processes=2) as pool:
        actual = _SemiAutoDoubler().wrap_func(_space(4), config, pool, offset=10)
    assert sorted(actual) == _EXPECTED
