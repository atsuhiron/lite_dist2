from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Annotated

from lite_dist2.expections import LD2TableNodeServerError
from lite_dist2.worker_node.table_node_client import TableNodeClient

if TYPE_CHECKING:
    from multiprocessing.pool import Pool

    from lite_dist2.config import WorkerConfig
    from lite_dist2.worker_node.trial_runner import BaseTrialRunner


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        trial_runner: Annotated[BaseTrialRunner, "Runner for executing trials"],
        ip: Annotated[str, "IP address of the table node server"],
        pool: Annotated[Pool | None, "Process pool for parallel execution. Ignored except `SemiAutoMPTrialRunner`."],
        config: Annotated[WorkerConfig, "Configuration of  the worker node"],
    ) -> None:
        self.trial_runner = trial_runner
        self.client = TableNodeClient(ip, config.name)
        self.pool = pool
        self.config = config

    def start(self) -> None:
        if not self.client.ping():
            msg = "Table node server not responding"
            raise LD2TableNodeServerError(msg)

        while True:
            self._step()

    def _step(self) -> None:
        trial = self.client.reserve_trial(
            self.config.max_size,
            self.config.retaining_capacity,
            self.config.table_node_request_timeout_seconds,
        )
        if trial is None:
            logger.info("No trial. Waiting %d seconds...", self.config.wait_seconds_on_no_trial)
            time.sleep(self.config.wait_seconds_on_no_trial)
            return
        self.trial_runner.run(trial, self.config, self.pool)
