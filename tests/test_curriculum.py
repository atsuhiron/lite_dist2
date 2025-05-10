from __future__ import annotations

import json
import pathlib
from typing import TYPE_CHECKING, Literal

import pytest

from lite_dist2.curriculum import Curriculum, CurriculumModel
from lite_dist2.study import Study, StudyModel, StudyStatus
from lite_dist2.study_storage import StudyStorage
from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel
from lite_dist2.suggest_strategies import BaseSuggestStrategy, SuggestStrategyModel
from lite_dist2.suggest_strategies.base_suggest_strategy import SuggestStrategyParam
from lite_dist2.trial import Mapping, TrialModel, TrialStatus
from lite_dist2.trial_table import TrialTable, TrialTableModel
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import ParameterRangeInt
from lite_dist2.value_models.point import ScalerValue
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


class MockStudyStrategyModel(StudyStrategyModel):
    type: Literal["all_calculation", "find_exact", "minimize", "test"] = "test"
    study_strategy_param: None = None


class MockStudyStrategy(BaseStudyStrategy):
    def __init__(self) -> None:
        super().__init__(None)

    def extract_mappings(self, trial_table: TrialTable) -> list[Mapping]:
        pass

    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        pass

    def to_model(self) -> StudyStrategyModel:
        pass


class MockSuggestStrategyModel(SuggestStrategyModel):
    type: Literal["sequential", "random", "designated", "test"] = "test"
    parameter: SuggestStrategyParam | None = None


class MockSuggestStrategy(BaseSuggestStrategy):
    def __init__(self) -> None:
        super().__init__(SuggestStrategyParam(strict_aligned=False), _DUMMY_PARAMETER_SPACE)

    def suggest(self, trial_table: TrialTable, max_num: int) -> ParameterSpace:
        pass

    def to_model(self) -> SuggestStrategyModel:
        pass


class MockStudy(Study):
    def __init__(self, study_id: str, done: bool) -> None:
        super().__init__(
            study_id,
            study_id,
            StudyStatus.reserved,
            DT,
            MockStudyStrategy(),
            MockSuggestStrategy(),
            _DUMMY_PARAMETER_SPACE,
            "scaler",
            "int",
            TrialTable([], None, 1),
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
            registered_timestamp=DT,
            done_timestamp=DT,
            result_type="scaler",
            result_value_type="int",
            result=[],
        )


@pytest.fixture
def done_study_fixture() -> MockStudy:
    return MockStudy(study_id="done_study", done=True)


@pytest.fixture
def not_done_study_fixture() -> MockStudy:
    return MockStudy(study_id="not_done_study", done=False)


def test_to_storage_if_done(done_study_fixture: MockStudy, not_done_study_fixture: MockStudy) -> None:
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
                status=StudyStatus.running,
                registered_timestamp=DT,
                study_strategy=StudyStrategyModel(type="all_calculation", study_strategy_param=None),
                suggest_strategy=SuggestStrategyModel(
                    type="sequential",
                    parameter=SuggestStrategyParam(strict_aligned=True),
                ),
                parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                result_type="scaler",
                result_value_type="int",
                trial_table=TrialTableModel(
                    trials=[
                        TrialModel(
                            study_id="01",
                            trial_id="01",
                            timestamp=DT,
                            trial_status=TrialStatus.done,
                            parameter_space=_DUMMY_PARAMETER_SPACE.to_model(),
                            result_type="scaler",
                            result_value_type="float",
                            result=[
                                Mapping(
                                    param=(
                                        ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                        ScalerValue(type="scaler", value_type="int", value="0x0", name="y"),
                                    ),
                                    result=ScalerValue(
                                        type="scaler",
                                        value_type="float",
                                        value="0x1.0000000000000p-1",
                                    ),
                                ),
                                Mapping(
                                    param=(
                                        ScalerValue(type="scaler", value_type="int", value="0x0", name="x"),
                                        ScalerValue(type="scaler", value_type="int", value="0x1", name="y"),
                                    ),
                                    result=ScalerValue(
                                        type="scaler",
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
                            result_type="scaler",
                            result_value_type="float",
                        ),
                    ],
                    aggregated_parameter_space={
                        -1: [],
                        0: [_DUMMY_PARAMETER_SPACE.to_model()],
                    },
                    timeout_minutes=1,
                ),
            ),
        ),
    ]
    storages = [
        StudyStorage(
            study_id="s2",
            name="s2",
            registered_timestamp=DT,
            done_timestamp=DT,
            result_type="scaler",
            result_value_type="int",
            result=[],
        ),
    ]
    return Curriculum(studies, storages)


def test_save_and_load(tmp_path: str, sample_curriculum_fixture: Curriculum) -> None:
    """save したデータを load_or_create で正しく読み込めるかをテスト"""
    json_path = pathlib.Path(f"{tmp_path}/curriculum.json")
    assert not json_path.exists()

    # save を実行
    sample_curriculum_fixture.save(json_path)

    # ファイルが作成されているか確認
    assert json_path.exists()

    # JSON の内容を確認
    with json_path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)

    # モデルのバリデーションを確認
    model = CurriculumModel.model_validate(json_data)
    assert model is not None

    # load_or_create を実行
    loaded_curriculum = Curriculum.load_or_create(json_path)

    # 元のデータと一致するか確認
    assert len(loaded_curriculum.studies) == len(sample_curriculum_fixture.studies)
    assert len(loaded_curriculum.storages) == len(sample_curriculum_fixture.storages)
    assert loaded_curriculum.studies[0].name == sample_curriculum_fixture.studies[0].name
    assert loaded_curriculum.storages[0].name == sample_curriculum_fixture.storages[0].name


def test_load_or_create_empty(tmp_path: str) -> None:
    json_path = pathlib.Path(f"{tmp_path}/non_existent.json")
    curriculum = Curriculum.load_or_create(json_path)

    assert isinstance(curriculum, Curriculum)
    assert len(curriculum.studies) == 0
    assert len(curriculum.storages) == 0
