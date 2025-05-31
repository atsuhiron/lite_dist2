from __future__ import annotations

import json
import pathlib
from typing import TYPE_CHECKING

import pytest

from lite_dist2.curriculum_models.curriculum import Curriculum, CurriculumModel
from lite_dist2.curriculum_models.study import Study
from lite_dist2.curriculum_models.study_portables import StudyModel, StudyStorage
from lite_dist2.curriculum_models.study_status import StudyStatus
from lite_dist2.curriculum_models.trial import Mapping, TrialModel, TrialStatus
from lite_dist2.curriculum_models.trial_table import TrialTable, TrialTableModel
from lite_dist2.expections import LD2ParameterError
from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel
from lite_dist2.study_strategies.all_calculation_study_strategy import AllCalculationStudyStrategy
from lite_dist2.suggest_strategies import BaseSuggestStrategy, SequentialSuggestStrategy, SuggestStrategyModel
from lite_dist2.suggest_strategies.base_suggest_strategy import SuggestStrategyParam
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.point import ScalarValue
from tests.const import DT

if TYPE_CHECKING:
    from lite_dist2.value_models.base_space import ParameterSpace

_DUMMY_PARAMETER_SPACE = ParameterAlignedSpace(
    axes=[
        ParameterRangeInt(name="x", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
        ParameterRangeInt(name="y", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
    ],
    check_lower_filling=True,
)

_DUMMY_STUDY_STRATEGY_MODEL = StudyStrategyModel(type="all_calculation", study_strategy_param=None)
_DUMMY_SUGGEST_STRATEGY_MODEL = SuggestStrategyModel(
    type="sequential",
    suggest_strategy_param=SuggestStrategyParam(strict_aligned=True),
)


class MockStudyStrategy(BaseStudyStrategy):
    def __init__(self) -> None:
        super().__init__(None)

    def extract_mappings(self, trial_table: TrialTable) -> list[Mapping]:
        pass

    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        pass

    def to_model(self) -> StudyStrategyModel:
        return _DUMMY_STUDY_STRATEGY_MODEL


class MockSuggestStrategy(BaseSuggestStrategy):
    def __init__(self) -> None:
        super().__init__(SuggestStrategyParam(strict_aligned=False), _DUMMY_PARAMETER_SPACE)

    def suggest(self, trial_table: TrialTable, max_num: int) -> ParameterSpace:
        pass

    def to_model(self) -> SuggestStrategyModel:
        return _DUMMY_SUGGEST_STRATEGY_MODEL


class MockStudy(Study):
    def __init__(self, study_id: str, done: bool) -> None:
        super().__init__(
            study_id,
            study_id,
            set(),
            StudyStatus.wait,
            DT,
            MockStudyStrategy(),
            MockSuggestStrategy(),
            _DUMMY_PARAMETER_SPACE,
            "scalar",
            "int",
            TrialTable([], None),
        )
        self.study_id = study_id
        self._done = done

    def is_done(self) -> bool:
        return self._done

    def update_status(self) -> None:
        pass

    def to_storage(self) -> StudyStorage:
        return StudyStorage(
            study_id=self.study_id,
            name=self.study_id,
            required_capacity=set(),
            registered_timestamp=DT,
            study_strategy=self.study_strategy.to_model(),
            suggest_strategy=self.suggest_strategy.to_model(),
            parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
            done_timestamp=DT,
            result_type="scalar",
            result_value_type="int",
            result=[],
            done_grids=4,
        )


@pytest.fixture
def done_study_fixture() -> MockStudy:
    return MockStudy(study_id="done_study", done=True)


@pytest.fixture
def not_done_study_fixture() -> MockStudy:
    return MockStudy(study_id="not_done_study", done=False)


def test_curriculum_to_storage_if_done(done_study_fixture: MockStudy, not_done_study_fixture: MockStudy) -> None:
    curriculum = Curriculum(studies=[done_study_fixture, not_done_study_fixture], storages=[])
    curriculum.to_storage_if_done()

    assert len(curriculum.studies) == 1
    assert len(curriculum.storages) == 1
    assert curriculum.studies[0].study_id == "not_done_study"
    assert curriculum.storages[0].study_id == "done_study"


@pytest.fixture
def sample_curriculum_fixture() -> Curriculum:
    studies = [
        Study.from_model(
            StudyModel(
                study_id="01",
                name="s1",
                required_capacity=set(),
                status=StudyStatus.running,
                registered_timestamp=DT,
                study_strategy=StudyStrategyModel(type="all_calculation", study_strategy_param=None),
                suggest_strategy=SuggestStrategyModel(
                    type="sequential",
                    suggest_strategy_param=SuggestStrategyParam(strict_aligned=True),
                ),
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                result_type="scalar",
                result_value_type="int",
                trial_table=TrialTableModel(
                    trials=[
                        TrialModel(
                            study_id="01",
                            trial_id="01",
                            timestamp=DT,
                            trial_status=TrialStatus.done,
                            parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                            result_type="scalar",
                            result_value_type="float",
                            worker_node_name="w01",
                            result=[
                                Mapping(
                                    param=(
                                        ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                                        ScalarValue(type="scalar", value_type="int", value="0x0", name="y"),
                                    ),
                                    result=ScalarValue(
                                        type="scalar",
                                        value_type="float",
                                        value="0x1.0000000000000p-1",
                                    ),
                                ),
                                Mapping(
                                    param=(
                                        ScalarValue(type="scalar", value_type="int", value="0x0", name="x"),
                                        ScalarValue(type="scalar", value_type="int", value="0x1", name="y"),
                                    ),
                                    result=ScalarValue(
                                        type="scalar",
                                        value_type="float",
                                        value="0x1.0000000000000p-2",
                                    ),
                                ),
                            ],
                        ),
                        TrialModel(
                            study_id="01",
                            trial_id="01",
                            timestamp=DT,
                            trial_status=TrialStatus.running,
                            parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                            result_type="scalar",
                            result_value_type="float",
                            worker_node_name="w01",
                        ),
                    ],
                    aggregated_parameter_space={
                        -1: [],
                        0: [_DUMMY_PARAMETER_SPACE.to_model()],
                    },
                ),
            ),
        ),
    ]
    storages = [
        StudyStorage(
            study_id="s2",
            name="s2",
            required_capacity=set(),
            registered_timestamp=DT,
            study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
            suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
            parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
            done_timestamp=DT,
            result_type="scalar",
            result_value_type="int",
            result=[],
            done_grids=4,
        ),
    ]
    return Curriculum(studies, storages)


def test_curriculum_save_and_load(tmp_path: str, sample_curriculum_fixture: Curriculum) -> None:
    json_path = pathlib.Path(f"{tmp_path}/curriculum.json")
    assert not json_path.exists()

    sample_curriculum_fixture.save(json_path)
    assert json_path.exists()

    with json_path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)
    model = CurriculumModel.model_validate(json_data)
    assert model is not None

    loaded_curriculum = Curriculum.load_or_create(json_path)
    assert len(loaded_curriculum.studies) == len(sample_curriculum_fixture.studies)
    assert len(loaded_curriculum.storages) == len(sample_curriculum_fixture.storages)
    assert loaded_curriculum.studies[0].name == sample_curriculum_fixture.studies[0].name
    assert loaded_curriculum.storages[0].name == sample_curriculum_fixture.storages[0].name


def test_curriculum_load_or_create_empty(tmp_path: str) -> None:
    json_path = pathlib.Path(f"{tmp_path}/non_existent.json")
    curriculum = Curriculum.load_or_create(json_path)

    assert isinstance(curriculum, Curriculum)
    assert len(curriculum.studies) == 0
    assert len(curriculum.storages) == 0


@pytest.mark.parametrize(
    ("retaining_capacity", "expected_study_id"),
    [
        pytest.param(
            {"hash", "preimage"},
            "hash_2",
            id="obtain running",
        ),
        pytest.param(
            {"hash"},
            "hash_1",
            id="obtain low required wait",
        ),
        pytest.param(
            {"mandelbrot"},
            None,
            id="obtain nothing",
        ),
    ],
)
def test_curriculum_get_available_study(retaining_capacity: set[str], expected_study_id: str | None) -> None:
    _study_param = {
        "name": "",
        "registered_timestamp": DT,
        "study_strategy": AllCalculationStudyStrategy(None),
        "suggest_strategy": SequentialSuggestStrategy(
            SuggestStrategyParam(strict_aligned=True),
            _DUMMY_PARAMETER_SPACE,
        ),
        "parameter_space": _DUMMY_PARAMETER_SPACE,
        "result_type": "scalar",
        "result_value_type": "int",
        "trial_table": TrialTable.from_model(TrialTableModel.create_empty()),
    }
    curriculum = Curriculum(
        studies=[
            Study(
                study_id="hash_1",
                required_capacity={"hash"},
                status=StudyStatus.wait,
                **_study_param,
            ),
            Study(
                study_id="hash_2",
                required_capacity={"hash", "preimage"},
                status=StudyStatus.running,
                **_study_param,
            ),
            Study(
                study_id="hash_3",
                required_capacity={"hash", "preimage"},
                status=StudyStatus.wait,
                **_study_param,
            ),
        ],
        storages=[],
    )

    study = curriculum.get_available_study(retaining_capacity)
    assert (study.study_id if study is not None else None) == expected_study_id


@pytest.mark.parametrize(
    ("study_id", "name", "expected_id", "expected_storages"),
    [
        pytest.param(
            "xxx",
            "xxx",
            None,
            [
                StudyStorage(
                    study_id="s01",
                    name="n01",
                    required_capacity=set(),
                    registered_timestamp=DT,
                    study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                    suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                    parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                    done_timestamp=DT,
                    result_type="scalar",
                    result_value_type="int",
                    result=[],
                    done_grids=4,
                ),
                StudyStorage(
                    study_id="s02",
                    name="n02",
                    required_capacity=set(),
                    registered_timestamp=DT,
                    study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                    suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                    parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                    done_timestamp=DT,
                    result_type="scalar",
                    result_value_type="int",
                    result=[],
                    done_grids=4,
                ),
            ],
            id="None",
        ),
        pytest.param(
            "s01",
            None,
            "s01",
            [
                StudyStorage(
                    study_id="s02",
                    name="n02",
                    required_capacity=set(),
                    registered_timestamp=DT,
                    study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                    suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                    parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                    done_timestamp=DT,
                    result_type="scalar",
                    result_value_type="int",
                    result=[],
                    done_grids=4,
                ),
            ],
            id="id pickup",
        ),
        pytest.param(
            None,
            "n02",
            "s02",
            [
                StudyStorage(
                    study_id="s01",
                    name="n01",
                    required_capacity=set(),
                    registered_timestamp=DT,
                    study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                    suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                    parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                    done_timestamp=DT,
                    result_type="scalar",
                    result_value_type="int",
                    result=[],
                    done_grids=4,
                ),
            ],
            id="name pickup",
        ),
        pytest.param(
            "s01",
            "n02",
            "s01",
            [
                StudyStorage(
                    study_id="s02",
                    name="n02",
                    required_capacity=set(),
                    registered_timestamp=DT,
                    study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                    suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                    parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                    done_timestamp=DT,
                    result_type="scalar",
                    result_value_type="int",
                    result=[],
                    done_grids=4,
                ),
            ],
            id="prior id",
        ),
    ],
)
def test_curriculum_pop_storage(
    study_id: str | None,
    name: str | None,
    expected_id: str | None,
    expected_storages: list[StudyStorage],
) -> StudyStorage | None:
    curr = Curriculum(
        studies=[],
        storages=[
            StudyStorage(
                study_id="s01",
                name="n01",
                required_capacity=set(),
                registered_timestamp=DT,
                study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                done_timestamp=DT,
                result_type="scalar",
                result_value_type="int",
                result=[],
                done_grids=4,
            ),
            StudyStorage(
                study_id="s02",
                name="n02",
                required_capacity=set(),
                registered_timestamp=DT,
                study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                done_timestamp=DT,
                result_type="scalar",
                result_value_type="int",
                result=[],
                done_grids=4,
            ),
        ],
    )

    popped = curr.pop_storage(study_id, name)
    if expected_id is None:
        assert popped is None
    else:
        assert popped.study_id == expected_id
    assert curr.storages == expected_storages


def test_curriculum_pop_storage_raises() -> None:
    curr = Curriculum(studies=[], storages=[])
    with pytest.raises(LD2ParameterError):
        _ = curr.pop_storage(None, None)


@pytest.mark.parametrize(
    ("study_id", "name", "expected"),
    [
        pytest.param("xxx", "xxx", StudyStatus.not_found, id="not_found"),
        pytest.param("s01", None, StudyStatus.done, id="done (storage) by id"),
        pytest.param(None, "n01", StudyStatus.done, id="done (storage) by name"),
        pytest.param("s04", None, StudyStatus.done, id="done (study) by id"),
        pytest.param(None, "n02", StudyStatus.running, id="running by name"),
        pytest.param("s03", None, StudyStatus.wait, id="wait by id"),
        pytest.param("s03", "n02", StudyStatus.wait, id="prior id"),
    ],
)
def test_curriculum_get_study_status(study_id: str | None, name: str | None, expected: StudyStatus) -> None:
    _study_param = {
        "required_capacity": {"hash"},
        "registered_timestamp": DT,
        "study_strategy": AllCalculationStudyStrategy(None),
        "suggest_strategy": SequentialSuggestStrategy(
            SuggestStrategyParam(strict_aligned=True),
            _DUMMY_PARAMETER_SPACE,
        ),
        "parameter_space": _DUMMY_PARAMETER_SPACE,
        "result_type": "scalar",
        "result_value_type": "int",
        "trial_table": TrialTable.from_model(TrialTableModel.create_empty()),
    }
    curr = Curriculum(
        studies=[
            Study(
                study_id="s02",
                name="n02",
                status=StudyStatus.running,
                **_study_param,
            ),
            Study(
                study_id="s03",
                name="n03",
                status=StudyStatus.wait,
                **_study_param,
            ),
            Study(
                study_id="s04",
                name="n04",
                status=StudyStatus.done,
                **_study_param,
            ),
        ],
        storages=[
            StudyStorage(
                study_id="s01",
                name="n01",
                required_capacity=set(),
                registered_timestamp=DT,
                study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                done_timestamp=DT,
                result_type="scalar",
                result_value_type="int",
                result=[],
                done_grids=4,
            ),
        ],
    )

    actual = curr.get_study_status(study_id, name)
    assert actual == expected


def test_curriculum_get_study_status_raises() -> None:
    curr = Curriculum(studies=[], storages=[])
    with pytest.raises(LD2ParameterError):
        _ = curr.get_study_status(None, None)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        pytest.param("n01", False),
        pytest.param("n02", False),
        pytest.param("n03", False),
        pytest.param("n04", False),
        pytest.param("n07", True),
        pytest.param(None, True),
    ],
)
def test_curriculum_try_insert_study(name: str | None, expected: bool) -> None:
    _study_param = {
        "required_capacity": {"hash"},
        "registered_timestamp": DT,
        "study_strategy": AllCalculationStudyStrategy(None),
        "suggest_strategy": SequentialSuggestStrategy(
            SuggestStrategyParam(strict_aligned=True),
            _DUMMY_PARAMETER_SPACE,
        ),
        "parameter_space": _DUMMY_PARAMETER_SPACE,
        "result_type": "scalar",
        "result_value_type": "int",
        "trial_table": TrialTable.from_model(TrialTableModel.create_empty()),
    }
    curr = Curriculum(
        studies=[
            Study(
                study_id="s02",
                name="n02",
                status=StudyStatus.running,
                **_study_param,
            ),
            Study(
                study_id="s03",
                name="n03",
                status=StudyStatus.wait,
                **_study_param,
            ),
            Study(
                study_id="s04",
                name="n04",
                status=StudyStatus.done,
                **_study_param,
            ),
            Study(
                study_id="s05",
                name=None,
                status=StudyStatus.done,
                **_study_param,
            ),
        ],
        storages=[
            StudyStorage(
                study_id="s01",
                name="n01",
                required_capacity=set(),
                registered_timestamp=DT,
                study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                done_timestamp=DT,
                result_type="scalar",
                result_value_type="int",
                result=[],
                done_grids=4,
            ),
            StudyStorage(
                study_id="s06",
                name=None,
                required_capacity=set(),
                registered_timestamp=DT,
                study_strategy=_DUMMY_STUDY_STRATEGY_MODEL,
                suggest_strategy=_DUMMY_SUGGEST_STRATEGY_MODEL,
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                done_timestamp=DT,
                result_type="scalar",
                result_value_type="int",
                result=[],
                done_grids=4,
            ),
        ],
    )
    new_study = Study(
        name=name,
        study_id="s07",
        status=StudyStatus.running,
        **_study_param,
    )
    actual = curr.try_insert_study(new_study)
    assert actual == expected
