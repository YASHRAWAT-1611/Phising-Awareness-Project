from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent

class UrlModel:
    def __init__(self):
        self.pipeline = joblib.load(BASE_DIR / "models" / "url_pipeline.joblib")

    def predict_proba(self, url: str) -> float:
        prob = self.pipeline.predict_proba([url])[0][1]
        return float(prob)
