# Runner used by the InterpreterPoolExecutor test. It lives in its own module on purpose:
# the executor pickles the runner instance and each subinterpreter re-imports this module by
# name, and pydantic_core cannot be imported in a subinterpreter. Do not import anything here
# that pulls in pydantic (lite_dist2.config, lite_dist2.worker_node.worker, curriculum_models, ...).
from lite_dist2.type_definitions import RawParamType, RawResultType
from lite_dist2.worker_node.trial_runner import SemiAutoMPTrialRunner


class InterpreterDoubler(SemiAutoMPTrialRunner):
    def func(self, parameters: RawParamType, *_args: object, **kwargs: object) -> RawResultType:
        offset = self.get_typed("offset", int, kwargs)
        return int(parameters[0]) * 2 + offset
