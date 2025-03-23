from pydantic import BaseModel

from lite_dist2.trial_table import TrialTable


class Study(BaseModel):
    study_id: str
    trial_table: TrialTable
    name: str | None

    def is_done(self) -> bool:
        pass
