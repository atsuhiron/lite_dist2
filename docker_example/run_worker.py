import asyncio
import signal
from concurrent.futures import ProcessPoolExecutor

from lite_dist2.config import WorkerConfig
from lite_dist2.type_definitions import RawParamType, RawResultType
from lite_dist2.worker_node.trial_runner import SemiAutoMPTrialRunner
from lite_dist2.worker_node.worker import Worker


def worker_init() -> None:
    # Ignore KeyboardInterrupt on worker processes
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class Mandelbrot(SemiAutoMPTrialRunner):
    def func(self, parameters: RawParamType, *_: object, **kwargs: object) -> RawResultType:
        abs_threshold = self.get_typed("abs_threshold", float, kwargs)
        max_iter = self.get_typed("max_iter", int, kwargs)
        x = float(parameters[0])
        y = float(parameters[1])
        c = complex(x, y)
        z = complex(0, 0)
        iter_count = 0
        while abs(z) <= abs_threshold and iter_count < max_iter:
            z = z**2 + c
            iter_count += 1
        return iter_count


async def main() -> None:
    worker_config = WorkerConfig(
        name="w_01",
        process_num=2,
        max_size=10,
        wait_seconds_on_no_trial=5,
        table_node_request_timeout_seconds=60,
    )
    with ProcessPoolExecutor(max_workers=2, initializer=worker_init) as pool:
        worker = Worker(
            trial_runner=Mandelbrot(),
            ip="table",  # Docker Compose でのサービス名
            port=8000,
            pool=pool,
            config=worker_config,
        )
        try:
            await worker.start_async(stop_at_no_trial=True)
        except KeyboardInterrupt:
            pool.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    asyncio.run(main())
