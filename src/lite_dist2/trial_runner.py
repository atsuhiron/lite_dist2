import abc
import dataclasses
from multiprocessing.pool import Pool

import tqdm

from lite_dist2.trial import Mapping, Trial
from lite_dist2.value_models.space import ParameterSpace


@dataclasses.dataclass(frozen=True)
class RunnerConfig:
    process_num: int | None = None
    disable_function_progress_bar: bool = False


class BaseTrialRunner(metaclass=abc.ABCMeta):
    def __init__(self, runner_config: RunnerConfig):
        self.runner_config = runner_config

    @abc.abstractmethod
    def func(self, *args):
        pass

    @abc.abstractmethod
    def wrap_func(self, parameter_space: ParameterSpace, pool: Pool | None) -> list[Mapping]:
        pass

    def run(self, trial: Trial, pool: Pool | None = None) -> Trial:
        result_list = self.wrap_func(trial.parameter_space, pool)
        trial = trial.create_new_with(result_list)
        return trial


class AutoMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def __init__(self, runner_config: RunnerConfig):
        super().__init__(runner_config)

    def wrap_func(self, parameter_space: ParameterSpace, _: Pool | None) -> list[Mapping]:
        mappings = []
        total = parameter_space.get_total()
        if self.runner_config.process_num > 1:
            with Pool(processes=self.runner_config.process_num) as pool:
                with tqdm.tqdm(total=total) as p_bar:
                    for arg_tuple, result in pool.imap_unordered(self.func, parameter_space.grid()):
                        parameter = parameter_space.value_tuple_to_param_type(arg_tuple)
                        mappings.append(Mapping(param=parameter, result=result))
                        p_bar.update(1)
            return mappings
        else:
            return [
                Mapping(param=parameter_space.value_tuple_to_param_type(arg_tuple), result=self.func(arg_tuple))
                for arg_tuple in tqdm.tqdm(parameter_space.grid(), total=total)
            ]


class ManualMPTrialRunner(BaseTrialRunner, metaclass=abc.ABCMeta):
    def __init__(self, runner_config: RunnerConfig):
        super().__init__(runner_config)

    def wrap_func(self, parameter_space: ParameterSpace, pool: Pool | None) -> list[Mapping]:
        mappings = []
        total = parameter_space.get_total()
        if self.runner_config.process_num > 1:
            with tqdm.tqdm(total=total) as p_bar:
                for arg_tuple, result in pool.imap_unordered(self.func, parameter_space.grid()):
                    parameter = parameter_space.value_tuple_to_param_type(arg_tuple)
                    mappings.append(Mapping(param=parameter, result=result))
                    p_bar.update(1)
            return mappings
        else:
            return [
                Mapping(param=parameter_space.value_tuple_to_param_type(arg_tuple), result=self.func(arg_tuple))
                for arg_tuple in tqdm.tqdm(parameter_space.grid(), total=total)
            ]
