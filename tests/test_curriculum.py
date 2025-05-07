from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from lite_dist2.curriculum import Curriculum
from lite_dist2.study import Study, StudyStatus
from lite_dist2.study_storage import StudyStorage
from lite_dist2.study_strategies import BaseStudyStrategy, StudyStrategyModel
from lite_dist2.suggest_strategies import BaseSuggestStrategy, SuggestStrategyModel
from lite_dist2.suggest_strategies.base_suggest_strategy import SuggestStrategyParam
from lite_dist2.trial_table import TrialTable
from lite_dist2.value_models.aligned_space import ParameterAlignedSpace
from lite_dist2.value_models.line_segment import ParameterRangeInt
from tests.const import DT

if TYPE_CHECKING:
    from lite_dist2.trial import Mapping
    from lite_dist2.value_models.base_space import ParameterSpace

_DUMMY_PARAMETER_SPACE = ParameterAlignedSpace(
    axes=[
        ParameterRangeInt(name="x", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
        ParameterRangeInt(name="y", type="int", size=2, start=0, ambient_size=2, ambient_index=0),
    ],
    check_lower_filling=True,
)


class MockStudyStrategy(BaseStudyStrategy):
    def __init__(self) -> None:
        super().__init__(None)

    def extract_mappings(self, trial_table: TrialTable) -> list[Mapping]:
        pass

    def is_done(self, trial_table: TrialTable, parameter_space: ParameterAlignedSpace) -> bool:
        pass

    def to_model(self) -> StudyStrategyModel:
        pass


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
def done_study() -> MockStudy:
    return MockStudy(study_id="done_study", done=True)


@pytest.fixture
def not_done_study() -> MockStudy:
    return MockStudy(study_id="not_done_study", done=False)


def test_to_storage_if_done(done_study: MockStudy, not_done_study: MockStudy) -> None:
    curriculum = Curriculum(studies=[done_study, not_done_study], storages=[])
    curriculum.to_storage_if_done()

    assert len(curriculum.studies) == 1
    assert len(curriculum.storages) == 1
    assert curriculum.studies[0].study_id == "not_done_study"
    assert curriculum.storages[0].study_id == "done_study"
