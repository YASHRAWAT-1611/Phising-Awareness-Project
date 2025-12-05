from pydantic import BaseModel, HttpUrl
from typing import List, Literal, Optional

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]

class TextAnalyzeRequest(BaseModel):
    text: str

class UrlAnalyzeRequest(BaseModel):
    url: str  # keep it string; you can validate yourself

class AnalysisResponse(BaseModel):
    risk: RiskLevel
    score: float
    reasons: List[str]
    advice: str
    type: Literal["text", "url"]
    ml_score: Optional[float] = None
