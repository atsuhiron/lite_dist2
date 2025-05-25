import asyncio
import logging
import socket
import threading

import uvicorn

from lite_dist2.config import TableConfigProvider
from lite_dist2.curriculum_models.curriculum import CurriculumProvider
from lite_dist2.table_node_api.api import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_local_ip() -> str:
    return socket.gethostbyname(socket.gethostname())


async def _periodic_save() -> None:
    interval = TableConfigProvider.get().curriculum_save_interval_seconds
    while True:
        await asyncio.sleep(interval)
        logger.info("Performing periodic save of curriculum data")
        await CurriculumProvider.save_async()


def _run_periodic_save() -> None:
    asyncio.run(_periodic_save())


async def _periodic_timeout_check() -> None:
    interval = TableConfigProvider.get().timeout_check_interval_seconds
    while True:
        await asyncio.sleep(interval)
        logger.info("Performing periodic timeout check of trials")
        await CurriculumProvider.check_timeout()


def _run_periodic_timeout_check() -> None:
    asyncio.run(_periodic_timeout_check())


def start() -> None:
    logger.info("Table Node IP: %s", _get_local_ip())

    # save thread
    save_thread = threading.Thread(target=_run_periodic_save, daemon=True)
    save_thread.start()

    # timeout check thread
    timeout_thread = threading.Thread(target=_run_periodic_timeout_check, daemon=True)
    timeout_thread.start()

    port = TableConfigProvider.get().port
    uvicorn.run(app, host="0.0.0.0", port=port)  # noqa: S104


def start_in_thread() -> None:
    table_thread = threading.Thread(target=start, daemon=True)
    table_thread.start()


if __name__ == "__main__":
    start()
