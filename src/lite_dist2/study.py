from pydantic import BaseModel


class Study(BaseModel):
    study_id: str
    trial_table: TrialTable
    name: str | None

    def is_done(self) -> bool:
        pass