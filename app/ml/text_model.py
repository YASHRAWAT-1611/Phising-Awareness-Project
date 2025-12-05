from pathlib import Path
import joblib
from typing import Tuple

BASE_DIR = Path(__file__).resolve().parent.parent

class TextModel:
    def __init__(self):
        self.pipeline = joblib.load(BASE_DIR / "models" / "text_pipeline.joblib")

    def predict_proba(self, text: str) -> float:
        # returns probability of being scam (label 1)
        prob = self.pipeline.predict_proba([text])[0][1]
        return float(prob)
