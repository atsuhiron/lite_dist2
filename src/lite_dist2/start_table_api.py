import asyncio
import logging
import socket
import threading

import uvicorn

from lite_dist2.api import app
from lite_dist2.config import ConfigProvider
from lite_dist2.curriculum_models.curriculum import CurriculumProvider

logger = logging.getLogger(__name__)


def _get_local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


async def periodic_save() -> None:
    time_out_seconds = ConfigProvider.table().default_timeout_minutes * 60
    while True:
        await asyncio.sleep(time_out_seconds)
        logger.info("Performing periodic save of curriculum data")
        await CurriculumProvider.save_async()


def run_periodic_save() -> None:
    asyncio.run(periodic_save())


async def start() -> None:
    logger.info("Table Node IP: %s", _get_local_ip())
    save_thread = threading.Thread(target=run_periodic_save, daemon=True)
    save_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104


if __name__ == "__main__":
    asyncio.run(start())
