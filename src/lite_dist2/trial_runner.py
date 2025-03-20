from typing import Callable
from multiprocessing.pool import Pool

import tqdm

from lite_dist2.trial import Trial
from lite_dist2.expections import LD2InvalidParameterError

class TrialRunner[TParam, TResult]:
    def __init__(
            self,
            func: Callable[[TParam], tuple[TParam, TResult]] | None,
            batch_func: Callable[[ParameterRange[TParam], Pool | None], list[tuple[TParam, TResult]]] | None,
            runner_config: RunnerConfig
    ):
        self.func = func
        self.batch_func = batch_func
        if self.batch_func is not None:
            self.use_batch = True
        elif self.func is not None:
            self.use_batch = False
        else:
            raise LD2InvalidParameterError("Specify at least one of func or batch_func.")
        self.runner_config = runner_config

    def run(self, trial: Trial, executor: Pool | None) -> Trial:
        if self.batch_func:
            result_list = self.batch_func(trial.parameter_range, executor)
        else:
            result_list = self._run(trial.parameter_range)
        trial = trial.apply_result(result_list)
        return trial

    def _run(self, parameter_range: ParamerterRange) -> list[Mapping]:
        mappings = []
        param_list = parameter_range.get_subspace()
        if self.runner_config.process_num > 1:
            with Pool(processes=self.runner_config) as executor:
                with tqdm.tqdm(total=parameter_range.get_size()) as p_bar:
                    for parameter, result in executor.imap_unordered(self.func, param_list):
                        mappings.append(Mappingg(parameter, result))
                        p_bar.update(1)
            return mappings
        else:
            return [Mapping(parameter, self.func(parameter)) for parameter in param_list]
