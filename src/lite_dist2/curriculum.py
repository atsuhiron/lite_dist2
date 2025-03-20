from pydantic import BaseModel

from lite_dist2.study import Study

class Curriculum(BaseModel):
    studies: list[Study]

    def get_current_study(self) -> Study | None:
        for study in self.studies:
            if study.is_done():
                return study
        return None