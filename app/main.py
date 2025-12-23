from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import TextAnalyzeRequest, UrlAnalyzeRequest, AnalysisResponse
from .ml.text_model import TextModel
from .ml.url_model import UrlModel
from .ml import text_rule_score, url_rule_score, risk_from_score

app = FastAPI(title="Phishing Scam Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

text_model = TextModel()
url_model = UrlModel()

@app.get("/")
def root():
    return {"status": "ok", "message": "Phishing Analyzer running"}

@app.post("/analyze/text", response_model=AnalysisResponse)
def analyze_text(req: TextAnalyzeRequest):
    ml_prob = text_model.predict_proba(req.text)  # probability scam
    rule_prob = text_rule_score(req.text)
    combined = 0.7 * rule_prob + 0.3 * ml_prob

    reasons = []
    if ml_prob > 0.6:
        reasons.append("ML model thinks this message is likely scam.")
    if rule_prob > 0.3:
        reasons.append("Contains suspicious words or requests (OTP/password/urgency).")

    risk = risk_from_score(combined)

    advice = {
        "HIGH": "Do NOT click any links or share any details. Ignore or delete this message.",
        "MEDIUM": "Be cautious. Verify via official channels (bank app, website, phone).",
        "LOW": "Looks mostly safe, but still avoid sharing sensitive data."
    }[risk]

    return AnalysisResponse(
        risk=risk,
        score=round(combined, 3),
        reasons=reasons or ["No major red flags, but always stay cautious."],
        advice=advice,
        type="text",
        ml_score=round(ml_prob, 3),
    )

@app.post("/analyze/url", response_model=AnalysisResponse)
def analyze_url(req: UrlAnalyzeRequest):
    ml_prob = url_model.predict_proba(req.url)
    rule_prob = url_rule_score(req.url)
    combined = 0.7 * rule_prob + 0.3 * ml_prob

    reasons = []
    if ml_prob > 0.6:
        reasons.append("ML model flags this URL as likely phishing.")
    if rule_prob > 0.3:
        reasons.append("URL structure looks suspicious (length, subdomains, keywords, etc.).")

    risk = risk_from_score(combined)

    advice = {
        "HIGH": "Do NOT open this link. Type official website manually or use app.",
        "MEDIUM": "Open only if you are 100% sure about the source. Prefer official app.",
        "LOW": "Seems mostly safe but avoid logging in via random links."
    }[risk]

    return AnalysisResponse(
        risk=risk,
        score=round(combined, 3),
        reasons=reasons or ["No strong signs of phishing, but stay alert."],
        advice=advice,
        type="url",
        ml_score=round(ml_prob, 3),
    )
