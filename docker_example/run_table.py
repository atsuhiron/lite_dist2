import os
from pathlib import Path

from lite_dist2.config import TableConfig, TableConfigProvider
from lite_dist2.table_node_api.start_table_api import start


def set_table_config() -> None:
    curriculum_dir = os.getenv("CURRICULUM_DIR", "/app")
    curriculum_path = Path(curriculum_dir) / "curriculum.json"

    config = TableConfig(
        port=8000,
        curriculum_path=curriculum_path,
        curriculum_save_interval_seconds=10,
    )
    TableConfigProvider.set(config)


if __name__ == "__main__":
    set_table_config()
    start()
