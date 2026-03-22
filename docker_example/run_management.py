import asyncio
import logging
import time

from lite_dist2.common import float2hex, int2hex
from lite_dist2.curriculum_models.study_portables import StudyRegistry
from lite_dist2.study_strategies import StudyStrategyModel
from lite_dist2.suggest_strategies import SuggestStrategyModel
from lite_dist2.suggest_strategies.base_suggest_strategy import SuggestStrategyParam
from lite_dist2.table_node_api.table_param import StudyRegisterParam
from lite_dist2.value_models.aligned_space_registry import LineSegmentRegistry, ParameterAlignedSpaceRegistry
from lite_dist2.value_models.const_param import ConstParam, ConstParamElement
from lite_dist2.worker_node.table_node_client import TableNodeClient

logger = logging.getLogger(__name__)


async def register_study(table_ip: str, table_port: int) -> None:
    _resolution = 10
    _half_size = 2.0

    study_register_param = StudyRegisterParam(
        study=StudyRegistry(
            name=f"mandelbrot-{int(time.time())}",
            required_capacity=set(),
            study_strategy=StudyStrategyModel(type="all_calculation", study_strategy_param=None),
            suggest_strategy=SuggestStrategyModel(
                type="sequential",
                suggest_strategy_param=SuggestStrategyParam(strict_aligned=True),
            ),
            result_type="scalar",
            result_value_type="int",
            const_param=ConstParam(
                consts=[
                    ConstParamElement(type="float", key="abs_threshold", value=float2hex(2.0)),
                    ConstParamElement(type="int", key="max_iter", value=int2hex(255)),
                ],
            ),
            parameter_space=ParameterAlignedSpaceRegistry(
                type="aligned",
                axes=[
                    LineSegmentRegistry(
                        name="x",
                        type="float",
                        size=int2hex(_resolution),
                        step=float2hex(2 * _half_size / _resolution),
                        start=float2hex(-1 * _half_size),
                    ),
                    LineSegmentRegistry(
                        name="y",
                        type="float",
                        size=int2hex(_resolution),
                        step=float2hex(2 * _half_size / _resolution),
                        start=float2hex(-1 * _half_size),
                    ),
                ],
            ),
        ),
    )
    client = TableNodeClient(table_ip, table_port)
    await client.register_study(study_register_param)
    logger.info("Study registered: %s", study_register_param.study.name)


async def main() -> None:
    # Wait for table node to be ready
    for i in range(30):
        try:
            await register_study(table_ip="table", table_port=8000)  # Docker Compose でのサービス名
            logger.info("Management: Study registration completed")
        except Exception as e:  # noqa: BLE001
            logger.warning("Waiting for table node... (%d/30): %s", i + 1, e)
            await asyncio.sleep(1)
        else:
            return

    logger.error("Failed to register study after 30 attempts")


if __name__ == "__main__":
    asyncio.run(main())
