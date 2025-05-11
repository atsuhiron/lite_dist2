import logging
import socket

import uvicorn

from lite_dist2.api import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def start() -> None:
    logger.info("Table Node IP: %s", get_local_ip())
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104


if __name__ == "__main__":
    start()
