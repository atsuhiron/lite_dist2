import json
import shutil

from lite_dist2.curriculum_models.trial import Trial, TrialModel
from lite_dist2.trial_repositories.base_trial_repository import BaseTrialRepository


class TrialRepository(BaseTrialRepository):
    def clean_save_dir(self) -> None:
        if self.save_dir.exists():
            for item in self.save_dir.iterdir():
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            self.save_dir.mkdir(parents=True, exist_ok=True)

    def save(self, trial: Trial) -> None:
        model = trial.to_model()
        path = self.save_dir / f"{trial.trial_id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(model.model_dump(mode="json"), f, ensure_ascii=False)

    def load(self, trial_id: str) -> Trial:
        path = self.save_dir / f"{trial_id}.json"
        with path.open("r", encoding="utf-8") as f:
            d = json.load(f, encoding="utf-8")
        return Trial.from_model(TrialModel.model_validate(d))

    def load_all(self) -> list[Trial]:
        trials = []
        if not self.save_dir.exists() or not self.save_dir.is_dir():
            raise FileNotFoundError(self.save_dir)

        for json_path in self.save_dir.glob("*.json"):
            with json_path.open("r", encoding="utf-8") as f:
                d = json.load(f)
                trials.append(Trial.from_model(TrialModel.model_validate(d)))
        return trials
